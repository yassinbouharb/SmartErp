# Graph Report - SmartErp  (2026-09-26)

## Corpus Check
- Corpus is ~5,660 words - fits in a single context window. You may not need a graph.

## Summary
- 177 nodes · 310 edges · 16 communities (8 shown, 8 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 14 edges (avg confidence: 0.94)
- Token cost: 3,387 input · 1,318 output

## Community Hubs (Navigation)
- Configuration and Utilities
- AI Agents and Services
- Business Logic Agents
- Document Generation System
- AI Services and Product Catalog
- Data Models and Schemas
- Customer Management System
- Templates and Document Output

## God Nodes (most connected - your core abstractions)
1. `CommandeFacture` - 16 edges
2. `ProduitCatalogue` - 12 edges
3. `trouver_table()` - 10 edges
4. `ClientRepository` - 9 edges
5. `ProduitRepository` - 9 edges
6. `col()` - 9 edges
7. `GeminiService` - 8 edges
8. `Article` - 8 edges
9. `Client` - 8 edges
10. `generate_invoice()` - 7 edges

## Surprising Connections (you probably didn't know these)
- `Invoice PDF FAC-2026-02` --semantically_similar_to--> `Facture Template`  [INFERRED] [semantically similar]
  facture/output/FAC-2026-02.pdf → facture/templates/template.html
- `Invoice PDF FAC-2026-03` --semantically_similar_to--> `Facture Template`  [INFERRED] [semantically similar]
  facture/output/FAC-2026-03.pdf → facture/templates/template.html
- `creer_BL_data()` --uses--> `CommandeBL`  [INFERRED]
  BL/generer.py → models/CommandeBL.py
- `GeminiService` --uses--> `CommandeFacture`  [INFERRED]
  ai/gemini_services.py → models/CommandeFacture.py
- `creer_facture_data()` --uses--> `CommandeFacture`  [INFERRED]
  facture/generer.py → models/CommandeFacture.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Document Generation System** — bl_templates_template, facture_templates_template, concept_invoice_data_structure [EXTRACTED 0.95]

## Communities (16 total, 8 thin omitted)

### Community 0 - "Configuration and Utilities"
Cohesion: 0.14
Nodes (13): GeminiService, Configuration du bot de facturation ==================================== Tu ne…, datetime, dotenv, google, openpyxl_utils, os, BLRepository (+5 more)

### Community 1 - "AI Agents and Services"
Cohesion: 0.08
Nodes (7): ProblemSolverAgent, ProductAgent, ConversationContext, ERPTools, dataclasses, openpyxl, FactureService

### Community 2 - "Business Logic Agents"
Cohesion: 0.10
Nodes (10): BL_agent, InvoiceAgent, ManagerAgent, idlelib, json, logging, CommandeFacture, BaseModel (+2 more)

### Community 3 - "Document Generation System"
Cohesion: 0.13
Nodes (19): base64, creer_BL_data(), generate_invoice(), html_to_pdf(), image_to_base64(), Path, Intègre le logo directement dans le HTML pour éviter les soucis d'accès file://…, render_html() (+11 more)

### Community 4 - "AI Services and Product Catalog"
Cohesion: 0.13
Nodes (13): GeminiExtractionError, GeminiService, GeminiService ============= Isole toute la logique d'appel à l'API Gemini :…, Levée quand Gemini ne renvoie pas un JSON exploitable ou invalide., Enrobe le client Gemini pour l'extraction de commandes en JSON structuré., Envoie la commande en langage naturel à Gemini et retourne un CommandeFacture…, enum, Exception (+5 more)

### Community 5 - "Data Models and Schemas"
Cohesion: 0.14
Nodes (15): Article, BaseModel, field_validator, Un article détecté dans la commande en langage naturel., CommandeBL, Devise, BaseModel, Enum (+7 more)

### Community 6 - "Customer Management System"
Cohesion: 0.27
Nodes (5): Client, BaseModel, ClientRepository, ClientService, typing

### Community 7 - "Templates and Document Output"
Cohesion: 0.50
Nodes (5): Bon de Livraison Template, Invoice/Delivery Data Structure, Invoice PDF FAC-2026-02, Invoice PDF FAC-2026-03, Facture Template

## Knowledge Gaps
- **2 isolated node(s):** `Invoice PDF FAC-2026-02`, `Invoice PDF FAC-2026-03`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 69 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `CommandeFacture` connect `Business Logic Agents` to `Document Generation System`, `AI Services and Product Catalog`, `Data Models and Schemas`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `Article` connect `Data Models and Schemas` to `Business Logic Agents`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `ProduitCatalogue` connect `AI Services and Product Catalog` to `Configuration and Utilities`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `CommandeFacture` (e.g. with `BL_agent` and `InvoiceAgent`) actually correct?**
  _`CommandeFacture` has 5 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ProduitCatalogue` (e.g. with `GeminiService` and `ProduitRepository`) actually correct?**
  _`ProduitCatalogue` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `ClientRepository` (e.g. with `Client` and `ClientService`) actually correct?**
  _`ClientRepository` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Invoice PDF FAC-2026-02`, `Invoice PDF FAC-2026-03` to the rest of the system?**
  _2 weakly-connected nodes found - possible documentation gaps or missing edges._