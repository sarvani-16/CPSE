package com.sih.material.service;

import com.sih.material.entity.Taxonomy;
import com.sih.material.repository.TaxonomyRepository;
import jakarta.annotation.PostConstruct;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

@Service
public class TaxonomyService {

    private final TaxonomyRepository taxonomyRepository;

    public TaxonomyService(TaxonomyRepository taxonomyRepository) {
        this.taxonomyRepository = taxonomyRepository;
    }

    @PostConstruct
    @Transactional
    public void seedDefaultTaxonomy() {
        if (taxonomyRepository.count() == 0) {
            // Level 1: Root Domains
            Taxonomy mech = taxonomyRepository.save(new Taxonomy("MECHANICAL", "Mechanical Equipment & Components", null, 1, "Piping, valves, fasteners, pumps and mechanical consumables"));
            Taxonomy elec = taxonomyRepository.save(new Taxonomy("ELECTRICAL", "Electrical Equipment & Switchgear", null, 1, "Cables, transformers, motors, switchgear, instrumentation"));
            Taxonomy civil = taxonomyRepository.save(new Taxonomy("CIVIL", "Civil & Structural Materials", null, 1, "Structural steel, cement, fabrication profiles"));

            // Level 2: Mechanical Subcategories
            taxonomyRepository.save(new Taxonomy("FASTENERS", "Industrial Fasteners & Hardware", "MECHANICAL", 2, "Bolts, nuts, studs, washers, screws"));
            taxonomyRepository.save(new Taxonomy("PIPING", "Pipes, Tubes & Fittings", "MECHANICAL", 2, "Seamless pipes, flanges, elbows, tees"));
            taxonomyRepository.save(new Taxonomy("VALVES", "Industrial Flow Valves", "MECHANICAL", 2, "Ball valves, gate valves, globe valves, check valves"));
            taxonomyRepository.save(new Taxonomy("SEALS", "Gaskets & Industrial Seals", "MECHANICAL", 2, "Spiral wound gaskets, O-rings, mechanical seals"));

            // Level 2: Electrical Subcategories
            taxonomyRepository.save(new Taxonomy("CABLES", "Power & Control Cables", "ELECTRICAL", 2, "Armoured copper cables, aluminum cables, control cables"));
            taxonomyRepository.save(new Taxonomy("SWITCHGEAR", "Switchgear & Circuit Breakers", "ELECTRICAL", 2, "VCBs, contactors, relays, isolators"));
            taxonomyRepository.save(new Taxonomy("MOTORS", "Electric Motors & Drives", "ELECTRICAL", 2, "Induction motors, VFDs, synchronous drives"));

            // Level 3: Fasteners Sub-items
            taxonomyRepository.save(new Taxonomy("BOLTS", "Hex Head & Stud Bolts", "FASTENERS", 3, "High tensile bolts, stainless steel bolts"));
            taxonomyRepository.save(new Taxonomy("NUTS", "Industrial Hex Nuts", "FASTENERS", 3, "Grade 8.8, 10.9, SS304/SS316 nuts"));
            taxonomyRepository.save(new Taxonomy("WASHERS", "Plain & Spring Washers", "FASTENERS", 3, "DIN 125, DIN 127 washers"));
        }
    }

    @Transactional(readOnly = true)
    public List<Map<String, Object>> getTaxonomyTree() {
        List<Taxonomy> all = taxonomyRepository.findAllByOrderByLevelAscCodeAsc();
        Map<String, Map<String, Object>> nodeMap = new LinkedHashMap<>();

        // Create tree structure
        for (Taxonomy t : all) {
            Map<String, Object> node = new LinkedHashMap<>();
            node.put("id", t.getId());
            node.put("code", t.getCode());
            node.put("name", t.getName());
            node.put("parent_code", t.getParentCode());
            node.put("level", t.getLevel());
            node.put("description", t.getDescription());
            node.put("children", new ArrayList<Map<String, Object>>());
            nodeMap.put(t.getCode(), node);
        }

        List<Map<String, Object>> rootNodes = new ArrayList<>();
        for (Taxonomy t : all) {
            Map<String, Object> node = nodeMap.get(t.getCode());
            if (t.getParentCode() == null || !nodeMap.containsKey(t.getParentCode())) {
                rootNodes.add(node);
            } else {
                @SuppressWarnings("unchecked")
                List<Map<String, Object>> children = (List<Map<String, Object>>) nodeMap.get(t.getParentCode()).get("children");
                children.add(node);
            }
        }

        return rootNodes;
    }

    @Transactional(readOnly = true)
    public List<Taxonomy> getAllTaxonomies() {
        return taxonomyRepository.findAllByOrderByLevelAscCodeAsc();
    }

    @Transactional
    public Taxonomy createTaxonomy(Taxonomy item) {
        if (taxonomyRepository.findByCodeIgnoreCase(item.getCode()).isPresent()) {
            throw new IllegalArgumentException("Taxonomy code already exists: " + item.getCode());
        }
        return taxonomyRepository.save(item);
    }
}
