package com.sih.material;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.sih.material.dto.CreateMaterialRequest;
import com.sih.material.dto.LoginRequest;
import com.sih.material.dto.RegisterRequest;
import com.sih.material.repository.SourceMaterialRepository;
import com.sih.material.repository.UserRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.nio.charset.StandardCharsets;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
@ActiveProfiles("h2")
public class UserDataIsolationTests {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private SourceMaterialRepository sourceMaterialRepository;

    @Test
    @DisplayName("Complete Section 6 Test: User A (TEST001) vs User B (TEST002) Real Persistent Data Isolation")
    void verifyUserSpecificDataIsolationLifecycle() throws Exception {
        // Step 0: Register User A (TEST001) and User B (TEST002)
        RegisterRequest regA = new RegisterRequest();
        regA.setEmployeeId("TEST001");
        regA.setName("User Alpha");
        regA.setEmail("alpha@ongc.co.in");
        regA.setPassword("AlphaPass123!");
        regA.setCpseName("ONGC");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(regA)))
                .andExpect(status().isOk());

        RegisterRequest regB = new RegisterRequest();
        regB.setEmployeeId("TEST002");
        regB.setName("User Beta");
        regB.setEmail("beta@bhel.in");
        regB.setPassword("BetaPass123!");
        regB.setCpseName("BHEL");

        mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(regB)))
                .andExpect(status().isOk());

        // 1. User A logs in
        LoginRequest loginA = new LoginRequest("TEST001", "AlphaPass123!");
        MvcResult loginResultA = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(loginA)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").isString())
                .andReturn();

        String tokenA = objectMapper.readTree(loginResultA.getResponse().getContentAsString()).get("token").asText();
        assertThat(tokenA).isNotBlank();

        // 2. User A creates/uploads data:
        // 2a. Direct material creation:
        CreateMaterialRequest matA1 = new CreateMaterialRequest("ONGC-MAT-001", "High Pressure Ball Valve 2 Inch Class 300", "ONGC");
        matA1.setMaterialGrade("SS316");
        matA1.setSpecification("API 6D");
        matA1.setUnitOfMeasure("EA");

        MvcResult createResultA1 = mockMvc.perform(post("/api/materials")
                        .header("Authorization", "Bearer " + tokenA)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(matA1)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.materialCode").value("ONGC-MAT-001"))
                .andReturn();

        JsonNode createdMatA1 = objectMapper.readTree(createResultA1.getResponse().getContentAsString());
        long matA1Id = createdMatA1.get("id").asLong();

        // 2b. Batch CSV upload by User A:
        String csvContentA = "material_code,description,specification,material_grade,dimensions,unit_of_measure,category\n" +
                "ONGC-CSV-101,Seamless Carbon Steel Pipe 3 Inch,ASTM A106 Gr B,Grade B,3 Inch Sch 40,MTR,Piping\n";
        MockMultipartFile csvFileA = new MockMultipartFile("file", "ongc_catalog.csv", "text/csv", csvContentA.getBytes(StandardCharsets.UTF_8));

        mockMvc.perform(multipart("/api/materials/upload")
                        .file(csvFileA)
                        .param("cpse_name", "ONGC")
                        .header("Authorization", "Bearer " + tokenA))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.status").value("SUCCESS"))
                .andExpect(jsonPath("$.imported_count").value(1));

        // Verify User A can view their 2 materials
        mockMvc.perform(get("/api/materials/source")
                        .header("Authorization", "Bearer " + tokenA))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(2))
                .andExpect(jsonPath("$.items[0].materialCode").exists());

        // Verify User A officer dashboard shows 2 materials
        mockMvc.perform(get("/api/dashboard/officer")
                        .header("Authorization", "Bearer " + tokenA))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.summary.my_materials").value(2));

        // 3. User A logs out
        mockMvc.perform(post("/api/auth/logout")
                        .header("Authorization", "Bearer " + tokenA))
                .andExpect(status().isOk());

        // 4. User B logs in
        LoginRequest loginB = new LoginRequest("TEST002", "BetaPass123!");
        MvcResult loginResultB = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(loginB)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.token").isString())
                .andReturn();

        String tokenB = objectMapper.readTree(loginResultB.getResponse().getContentAsString()).get("token").asText();
        assertThat(tokenB).isNotBlank();

        // 5. User B CANNOT see User A's data!
        // 5a. User B's catalog list returns 0 materials (none belonging to User B yet)
        mockMvc.perform(get("/api/materials/source")
                        .header("Authorization", "Bearer " + tokenB))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(0))
                .andExpect(jsonPath("$.items").isEmpty());

        // 5b. User B attempting to view User A's material ID returns 404
        mockMvc.perform(get("/api/materials/" + matA1Id)
                        .header("Authorization", "Bearer " + tokenB))
                .andExpect(status().isNotFound());

        // 5c. User B's officer dashboard shows 0 materials
        mockMvc.perform(get("/api/dashboard/officer")
                        .header("Authorization", "Bearer " + tokenB))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.summary.my_materials").value(0));

        // 6. User B creates data
        CreateMaterialRequest matB1 = new CreateMaterialRequest("BHEL-TURB-501", "Heavy Steam Turbine Blade Rotor Assembly", "BHEL");
        matB1.setMaterialGrade("Inconel 718");
        matB1.setSpecification("DIN 17240");
        matB1.setUnitOfMeasure("SET");

        MvcResult createResultB1 = mockMvc.perform(post("/api/materials")
                        .header("Authorization", "Bearer " + tokenB)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(matB1)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.materialCode").value("BHEL-TURB-501"))
                .andReturn();

        JsonNode createdMatB1 = objectMapper.readTree(createResultB1.getResponse().getContentAsString());
        long matB1Id = createdMatB1.get("id").asLong();

        // Verify User B sees only their 1 material
        mockMvc.perform(get("/api/materials/source")
                        .header("Authorization", "Bearer " + tokenB))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(1))
                .andExpect(jsonPath("$.items[0].materialCode").value("BHEL-TURB-501"));

        // 7. User A logs in again (persistent account & session test)
        LoginRequest loginA2 = new LoginRequest("TEST001", "AlphaPass123!");
        MvcResult loginResultA2 = mockMvc.perform(post("/api/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(loginA2)))
                .andExpect(status().isOk())
                .andReturn();

        String tokenA2 = objectMapper.readTree(loginResultA2.getResponse().getContentAsString()).get("token").asText();

        // 8. User A can still see their original data
        mockMvc.perform(get("/api/materials/source")
                        .header("Authorization", "Bearer " + tokenA2))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.total").value(2));

        mockMvc.perform(get("/api/materials/" + matA1Id)
                        .header("Authorization", "Bearer " + tokenA2))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.material_code").value("ONGC-MAT-001"));

        // 9. User B's data is NOT visible to User A
        mockMvc.perform(get("/api/materials/" + matB1Id)
                        .header("Authorization", "Bearer " + tokenA2))
                .andExpect(status().isNotFound());

        // Verify User A CSV export contains User A items and NOT User B items
        MvcResult exportA = mockMvc.perform(get("/api/materials/export")
                        .header("Authorization", "Bearer " + tokenA2))
                .andExpect(status().isOk())
                .andReturn();

        String exportCsvA = exportA.getResponse().getContentAsString();
        assertThat(exportCsvA).contains("ONGC-MAT-001");
        assertThat(exportCsvA).doesNotContain("BHEL-TURB-501");
    }
}
