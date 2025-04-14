# Approach & Assumptions

## Approach

- **Lightweight modeling**  
  The data processing logic uses list-based models to enable fast iteration and easy prototyping.
  In a production environment, I would have considered to use more structred representation through `dataclasses` for readability, type enforcement, maintainability, ecc.

- **Event-Driven state**  
  Entity states depends on the `eventType` field in incoming data:
  - `CREATE` → INSERT record  
  - `UPDATE` → MODIFY record  
  - `DELETE` → REMOVE record

  The idea is to replicate the behaviour of an event sourced systems, where state is reconstructed from a stream of changes

- **SQLite as storage solution**  
  SQLite is used to store tables for simplicity and ease of setup.
  In production, this would likely be replaced by a more scalable solution like PostgreSQL, Delta Tables, Amazon Redshift.

- **Mapping of interesting fields only**  
  Only a subset of the available fields are mapped in the current model. 
  For instance, `deviceTags` and similar nested fields have been skipped.  
---

## Assumptions

- **Batch processing**  
  The pipeline assumes a batch processing model, where a JSON payload is received and processed periodically (e.g., every x mins or hours)

- **Stateless pipeline**  
  Each run is stateless and relies entirely on incoming data only to derive the current state

---

## Potential Improvements

- **Schema validation**  
  Add JSON schema validation  through `jsonschema` for instance to catch malformed or incomplete records early in the pipeline

- **Error handling/logging**  
  Implement structureed logging and robust error handling around parsing, transformation, and database operations

- **Incremental load and partitioning**  
  In production env, I would implemnt support for incremental loading using timestamps or watermarks, and optionally partition data for scalability

---