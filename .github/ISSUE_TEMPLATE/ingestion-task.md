---
name: Ingestion task
about: Add ingestion task for a new website source
title: FEAT
labels: ''
assignees: ''
---

1. **Ensure you're on the latest `main` branch:**

```bash
git checkout main
git pull
````

2. **Create a new feature branch:**

```bash
git checkout -b add-ingestion-<website>
```

3. **Start your Docker environment:**

```bash
make up-build
make sh
```

4. **Create the ingestion script file:**

```bash
touch etls/extract_<website>.py -p
```

5. **Write your ingestion script**
Implement logic to extract and return the required data from `<website>`.

6. **Create a test file for your script:**

```bash
touch test/test_etls/extract_<website>.py -p
```

7. **Write tests for your ingestion script**
Make sure to cover expected input/output and edge cases.

8. **Commit your changes and push the branch:**

```bash
git add .
git commit -m "feat(ingestion) ingestion script for <website>"
git push
```

9. **Create a pull request to `main` and request review.**
