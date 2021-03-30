### The purpose of the code changes are as follows:
-  THING

**How to prepare for test**:
- `cd MUTANT`
- `export PATH=$PATH:MUTANT_DIR`
- `source activate CONDA_ENV`
- `pip install .`

### How to test:
- `mutant analyse sarscov2 tests/testdata/fasta_files --profiles local,singularity --config_artic mutant/config/local/artic.json`

### Expected outcome:
- [ ] Produced files contain expected values

### Review:
- [ ] Code reviewed by

This [version](https://semver.org/) is a:
- [ ] **MAJOR** - when you make incompatible API changes
- [ ] **MINOR** - when you add functionality in a backwards compatible manner
- [ ] **PATCH** - when you make backwards compatible bug fixes or documentation/instructions
