# PharmaShield India AI: Premium Pharmacy Intelligence

PharmaShield India AI is a state-of-the-art, memory-aware multi-agent RAG platform tailored specifically for the Indian healthcare and pharmaceutical ecosystem. Built on a polyglot persistence architecture (PostgreSQL + MongoDB) and powered by an advanced orchestration engine, it provides critical intelligence across the entire medication lifecycle.

## 🚀 Key Features

- **India-Specific Compliance**: Intelligent Schedule H/H1/X verification and automated CDSCO NSQ (Not of Standard Quality) batch matching.
- **Affordability Engine**: Integrated NPPA price checking and Jan Aushadhi generic alternative discovery.
- **Multi-Agent Orchestration**: Dynamic coordination of 6+ specialized agents (Price, Compliance, NSQ, Seller-Risk, Scheme, Inventory).
- **Advanced RAG Pipeline**: Citation-backed document analysis for prescriptions, lab reports, and clinical summaries.
- **Role-Based Intelligence**:
    - **👤 Patient**: Simple report explanations, affordability guidance, and safe next steps.
    - **💊 Pharmacist**: Professional dispensing checks, stock verification, and substitution caution.
    - **🩺 Doctor**: Clinical case synthesis, patient safety highlights, and follow-up considerations.
    - **⚙️ Admin**: System-wide analytics, risk monitoring, and comprehensive audit logs.

## 🏗️ Architecture

- **Backend**: Python (FastAPI) + PostgreSQL (Compliance/Audit) + MongoDB (Cases/Documents) + Qdrant (Vector Store).
- **Frontend**: Next.js 15 + TailwindCSS + Premium Dark Theme.
- **Security**: Role-based access control, medical safety guardrails, and automated audit trails.

## 🛠️ Quickstart

1. **Environment Setup**:
   ```bash
   cp .env.example .env
   # Update .env with your database URIs and OpenAI API key
   ```

2. **Launch with Docker**:
   ```bash
   make up
   ```

3. **Seed Demo Users (required for login)**:
   ```bash
   make seed-users
   ```

4. **Access the Portals**:
   - **Frontend**: [http://localhost:3000](http://localhost:3000)
   - **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)

5. **Verify System**:
   ```bash
   # Run unit tests (logic & RBAC)
   make test-unit
   
   # Run integration tests (requires full DB)
   make test-integration
   ```

---
*Built for the future of Indian Healthcare.*
