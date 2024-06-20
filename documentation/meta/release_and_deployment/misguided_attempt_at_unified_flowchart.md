```{mermaid}
flowchart TD
    Merge[Merge to main]
    Build("<u>CI/CD</u>\nVerify code, build/upload docker images\ntagged with <code>latest</code> and the commit hash")
    StagingDispatch("<u>API/Frontend</u>\nDispatch production\ndeployment workflow;\n renders & pushes task definition\nwith commit hash tag")
    DagSync("<u>Catalog</u>\nDAG Sync script pulls new\ncode from GitHub which is\nautomatically parsed by Airflow\nand used for new runs")
    IdxWorker("<u>Indexer worker</u>\nNew EC2 instances pull\nthe <code>latest</code> tagged\nimage next time they run")
    RevertRollback[Roll back by merging a revert\nof the broken code to main] ---> Build

    Merge ---> Build

    Build --> StagingDispatch o--o RevertRollback
    Build --> DagSync o--o RevertRollback
    Build --> IdxWorker o--o RevertRollback

    StagingDispatch -.-> Publish
    DagSync -..-> Publish

    Publish[Publish GitHub Release]
    Tag("Tag the <code>latest</code> docker image for the\nreleased app with the 'release tag' based\non the GitHub Release title and associated git tag")
    ProductionDispatch("<u>API/Frontend</u>\nDispatch production\ndeployment workflow;\n renders & pushes task definition\nwith commit hash tag")
    ManCat["<u>Catalog</u>\nAdd the release tag to the catalog's\nAnsible variables and run the catalog's\nAnsible playbook</u>"]
    IngestionServer["<u>Ingestion server</u>\nAdd the release tag to the ingestion server's\nTerraform variables and run terraform apply"]
    TriggerRollback[Trigger the production deployment\nworkflow with the last known\nworking production image tag]
    ApplyRollback[Redo the previous step, but with the last\nknown working production image tag]

    Publish --> Tag
    Tag --> ProductionDispatch o--o|Rollback| TriggerRollback
    Tag ---> ManCat o--o|Rollback| ApplyRollback
    Tag --> IngestionServer o--o|Rollback| ApplyRollback
```
