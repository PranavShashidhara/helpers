# Invoke Workflows

<!-- toc -->

- [Introduction](#introduction)
  * [Listing All the Tasks](#listing-all-the-tasks)
  * [Getting Help for a Specific Workflow](#getting-help-for-a-specific-workflow)
  * [Implementation Details](#implementation-details)
- [Git](#git)
  * [Merge Master in the Current Branch](#merge-master-in-the-current-branch)
- [Github](#github)
  * [Create a PR](#create-a-pr)
  * [Extract a PR From a Larger One](#extract-a-pr-from-a-larger-one)
  * [Systematic Code Transformation](#systematic-code-transformation)
  * [Generate a Local `amp` Docker Image](#generate-a-local-amp-docker-image)
- [Update the dev `amp` Docker image](#update-the-dev-amp-docker-image)
- [Experiment in a local image](#experiment-in-a-local-image)
- [Github Actions (CI)](#github-actions-ci)
- [Pytest](#pytest)
  * [Run with Coverage](#run-with-coverage)
  * [Capture Output of a Pytest](#capture-output-of-a-pytest)
  * [Run Only One Test Based on Its Name](#run-only-one-test-based-on-its-name)
  * [Iterate on Stacktrace of Failing Test](#iterate-on-stacktrace-of-failing-test)
  * [Iterating on a Failing Regression Test](#iterating-on-a-failing-regression-test)
  * [Detect Mismatches with Golden Test Outcomes](#detect-mismatches-with-golden-test-outcomes)
- [Lint](#lint)
  * [Lint Everything](#lint-everything)

<!-- tocstop -->

## Introduction

- We use `invoke` to implement workflows (aka "tasks") similar to Makefile
  targets, but using Python
- The official documentation for `invoke` is
  [here](https://docs.pyinvoke.org/en/0.11.1/index.html)

- We use `invoke` to automate tasks and package workflows for:
  - Docker: `docker_*`
  - Git: `git_*`
  - GitHub (relying on `gh` integration): `gh_*`
  - Running tests: `run_*`
  - Branch integration: `integrate_*`
  - Releasing tools and Docker images: `docker_*`
  - Lint: `lint_*`

- Each set of commands starts with the name of the corresponding topic:
  - E.g., `docker_*` for all the tasks related to Docker
- The best approach to getting familiar with the tasks is to browse the list and
  then check the output of the help
- `i` is the shortcut for the `invoke` command

  ```bash
  > invoke --help command
  > i -h gh_issue_title
  Usage: inv[oke] [--core-opts] gh_issue_title [--options] [other tasks here ...]

  Docstring:
  Print the title that corresponds to the given issue and repo_short_name.
  E.g., AmpTask1251_Update_GH_actions_for_amp.

  :param pbcopy: save the result into the system clipboard (only on macOS)

  Options:
  -i STRING, --issue-id=STRING
  -p, --[no-]pbcopy
  -r STRING, --repo-short-name=STRING
  ```

- We can guarantee you a 2x improvement in performance if you master the
  workflows, but it takes some time and patience

- `TAB` completion available for all the tasks, e.g.,

  ```bash
  > i gh_<TAB>
  gh_create_pr      gh_issue_title    gh_login          gh_workflow_list  gh_workflow_run
  ```
  - Tabbing after typing a dash (-) or double dash (--) will display valid
    options/flags for the current context.

### Listing All the Tasks

- New commands are always being added, but a list of valid tasks is below

  ````bash
  > invoke --list
  INFO: > cmd='/Users/saggese/src/venv/amp.client_venv/bin/invoke --list'
  Available tasks:
  copy_ecs_task_definition_image_url                    Copy image URL from one task definition to another.

  docker_bash                                           Start a bash shell inside the container corresponding to a stage.
  docker_build_local_image                              Build a local image, i.e., a release candidate "dev" image.
  docker_build_prod_image                               Build a prod image from a dev image.
  docker_cmd                                            Execute the command `cmd` inside a container corresponding to a stage.
  docker_create_candidate_image                         Create new prod candidate image and update the specified ECS task
  docker_images_ls_repo                                 List images in the logged in repo_short_name.
  docker_jupyter                                        Run Jupyter notebook server.
  docker_kill                                           Kill the last Docker container started.
  docker_login                                          Log in the target registry and skip if we are in kaizenflow.
  docker_ps                                             List all the running containers.
  docker_pull                                           Pull latest dev image corresponding to the current repo from the registry.
  docker_pull_helpers                                   Pull latest prod image of `helpers` from the registry.
  docker_push_dev_image                                 Push the "dev" image to ECR.
  docker_push_prod_candidate_image                      (ONLY CI/CD) Push the "prod" candidate image to ECR.
  docker_push_prod_image                                Push the "prod" image to ECR.
  docker_release_dev_image                              Build, test, and release to ECR the latest "dev" image.
  docker_release_multi_build_dev_image                  Build, test, and release the latest multi-arch "dev" image.
  docker_release_prod_image                             Build, test, and release to ECR the prod image.
  docker_rollback_dev_image                             Rollback the version of the dev image.
  docker_rollback_prod_image                            Rollback the version of the prod image.
  docker_stats                                          Report last started Docker container stats, e.g., CPU, RAM.
  docker_tag_local_image_as_dev                         Mark the "local" image as "dev".
  docker_tag_push_multi_build_local_image_as_dev        Mark the multi-arch "local" image as "dev" and push it.
  docker_update_prod_task_definition                    Update image in prod task definition to the desired version.

  find                                                  Find symbols, imports, test classes and so on.
  find_check_string_output                              Find output of `check_string()` in the test running
  find_dependency                                       E.g., ```
  find_test_class                                       Report test files containing `class_name` in a format compatible with
  find_test_decorator                                   Report test files containing `class_name` in pytest format.

  fix_perms                                             :param action:

  gh_create_pr                                          Create a draft PR for the current branch in the corresponding
  gh_issue_title                                        Print the title that corresponds to the given issue and repo_short_name.
  gh_login
  gh_publish_buildmeister_dashboard_to_s3               Run the buildmeister dashboard notebook and publish it to S3.
  gh_workflow_list                                      Report the status of the GH workflows.
  gh_workflow_run                                       Run GH workflows in a branch.

  git_add_all_untracked                                 Add all untracked files to Git.
  git_branch_copy                                       Create a new branch with the same content of the current branch.
  git_branch_create                                     Create and push upstream branch `branch_name` or the one corresponding to
  git_branch_delete_merged                              Remove (both local and remote) branches that have been merged into master.
  git_branch_diff_with                                  Diff files of the current branch with master at the branching point.
  git_branch_files                                      Report which files were added, changed, and modified in the current branch
  git_branch_next_name                                  Return a name derived from the current branch so that the branch doesn't
  git_branch_rename                                     Rename current branch both locally and remotely.
  git_clean                                             Clean the repo_short_name and its submodules from artifacts.
  git_fetch_master                                      Pull master without changing branch.
  git_files                                             Report which files are changed in the current branch with respect to
  git_last_commit_files                                 Print the status of the files in the previous commit.
  git_merge_master                                      Merge `origin/master` into the current branch.
  git_patch_create                                      Create a patch file for the entire repo_short_name client from the base
  git_pull                                              Pull all the repos.
  git_roll_amp_forward                                  Roll amp forward.

  integrate_create_branch                               Create the branch for integration of `dir_basename` (e.g., amp1) in the
  integrate_diff_dirs                                   Integrate repos from dirs `src_dir_basename` to `dst_dir_basename` by diffing
  integrate_diff_overlapping_files                      Find the files modified in both branches `src_dir_basename` and
  integrate_file                                        Diff corresponding files in two different repos.
  integrate_files                                       Find and copy the files that are touched only in one branch or in both.
  integrate_find_files                                  Find the files that are touched in the current branch since last
  integrate_find_files_touched_since_last_integration   Print the list of files modified since the last integration for this dir.
  integrate_rsync                                       Use `rsync` to bring two dirs to sync.

  lint                                                  Lint files.
  lint_check_if_it_was_run                              Check if Linter was run in the current branch.
  lint_check_python_files                               Compile and execute Python files checking for errors.
  lint_check_python_files_in_docker                     Compile and execute Python files checking for errors.
  lint_create_branch                                    Create the branch for linting in the current dir.
  lint_detect_cycles                                    Detect cyclic imports in the directory files.

  print_env                                             Print the repo configuration.
  print_setup                                           Print some configuration variables.
  print_tasks                                           Print all the available tasks in `lib_tasks.py`.

  pytest_add_untracked_golden_outcomes                  Add the golden outcomes files that are not tracked under git.
  pytest_buildmeister                                   Run the regression tests.
  pytest_buildmeister_check                             :param print_output: print content of the file with the output of the
  pytest_clean                                          Clean pytest artifacts.
  pytest_collect_only
  pytest_compare_logs                                   Diff two log files removing the irrelevant parts (e.g., timestamps, object
  pytest_find_unused_goldens                            Detect mismatches between tests and their golden outcome files.
  pytest_rename_test                                    Rename the test and move its golden outcome.
  pytest_repro                                          Generate commands to reproduce the failed tests after a `pytest` run.

  release_dags_to_airflow                               Copy the DAGs to the shared Airflow directory.

  run_blank_tests                                       (ONLY CI/CD) Test that pytest in the container works.
  run_coverage_report                                   Compute test coverage stats.
  run_coverage_subprocess                               Run comprehensive coverage using subprocess mode with hcoverage injection and direct
                                                        coverage run.
  run_fast_slow_superslow_tests                         Run fast, slow, superslow tests back-to-back.
  run_fast_slow_tests                                   Run fast and slow tests back-to-back.
  run_fast_tests                                        Run fast tests. check `gh auth status` before invoking to avoid auth
  run_qa_tests                                          Run QA tests independently.
  run_slow_tests                                        Run slow tests.
  run_superslow_tests                                   Run superslow tests.
  run_tests                                             :param test_lists: comma separated list with test lists to run (e.g., `fast_test,slow_tests`)

  traceback                                             Parse the traceback from Pytest and navigate it with vim.
  ````

### Getting Help for a Specific Workflow

- You can get a more detailed help with

  ```bash
  > invoke --help run_fast_tests
  Usage: inv[oke] [--core-opts] run_fast_tests [--options] [other tasks here ...]

  Docstring:
  Run fast tests.

  :param stage: select a specific stage for the Docker image
  :param pytest_opts: option for pytest
  :param pytest_mark: test list to select as `@pytest.mark.XYZ`
  :param dir_name: dir to start searching for tests
  :param skip_submodules: ignore all the dir inside a submodule
  :param coverage: enable coverage computation
  :param collect_only: do not run tests but show what will be executed

  Options:
  -c, --coverage
  -d STRING, --dir-name=STRING
  -k, --skip-submodules
  -o, --collect-only
  -p STRING, --pytest-opts=STRING
  -s STRING, --stage=STRING
  -y STRING, --pytest-mark=STRING
  ```

### Implementation Details

- By convention all invoke targets are in `*_lib_tasks.py`, e.g.,
  - `helpers/lib_tasks.py` - tasks to be run in `cmamp`
  - `optimizer/opt_lib_tasks.py` - tasks to be run in `cmamp/optimizer`
- All invoke tasks are functions with the `@task` decorator, e.g.,

  ```python
  from invoke import task

  @task
  def invoke_task(...):
    ...
  ```

- To run a task we use `context.run(...)`, see
  [the official docs](https://docs.pyinvoke.org/en/0.11.1/concepts/context.html)
- To be able to run a specified invoke task one should import it in `tasks.py`
  - E.g., see `cmamp/tasks.py`
- A task can be run only in a dir where it is imported in a corresponding
  `tasks.py`, e.g.,
  - `invoke_task1` is imported in `cmamp/tasks.py` so it can be run only from
    `cmamp`
  - `invoke_task2` is imported in `cmamp/optimizer/tasks.py` so it can be run
    only from `cmamp/optimizer`
    - In other words one should do `cd cmamp/optimizer` before doing
      `i invoke_task2 ...`

## Git

### Merge Master in the Current Branch

```bash
> i git_merge_master
```

## Github

- Get the official branch name corresponding to an Issue

  ```bash
  > i gh_issue_title -i 256
  ## gh_issue_title: issue_id='256', repo_short_name='current'

  # Copied to system clipboard:
  AmpTask256_Part_task2236_jenkins_cleanup_split_scripts:
  https://github.com/alphamatic/amp/pull/256
  ```

### Create a PR

TODO(gp): Describe

### Extract a PR From a Larger One

- For splitting large PRs, use the dedicated workflow `git_branch_copy'
- See detailed guide in
  [all.invoke_git_branch_copy.how_to_guide.md](/docs/tools/all.invoke_git_branch_copy.how_to_guide.md)

### Systematic Code Transformation

- Can be done with the help of
  `dev_scripts_helpers/system_tools/replace_text.py`

### Generate a Local `amp` Docker Image

- This is a manual flow used to test and debug images before releasing them to
  the team.
- The flow is similar to the dev image, but by default tests are not run and the
  image is not released.

  ```bash
  # Build the local image (and update Poetry dependencies, if needed).

  > i docker_build_local_image --update-poetry
  ...
  docker image ls 665840871993.dkr.ecr.us-east-1.amazonaws.com/amp:local

  REPOSITORY TAG IMAGE ID CREATED SIZE
  665840871993.dkr.ecr.us-east-1.amazonaws.com/amp local 9b3f8f103a2c 1 second ago 1.72GB

  # Test the new "local" image
  > i docker_bash --stage "local" python -c "import async_solipsism" python -c
  > "import async_solipsism; print(async_solipsism.**version**)"

  # Run the tests with local image
  # Make sure the new image is used: e.g., add an import and trigger the tests.
  > i run_fast_tests --stage "local" --pytest-opts core/dataflow/test/test_real_time.py
  > i run_fast_slow_tests --stage "local"

  # Promote a local image to dev.
  > i docker_tag_local_image_as_dev
  > i docker_push_dev_image
  ```

  ## Update the dev `amp` Docker image

- To implement the entire Docker QA process of a dev image

  ```bash
  # Clean all the Docker images locally, to make sure there is no hidden state.
  > docker system prune --all

  # Update the needed packages.
  > devops/docker_build/pyproject.toml

  # Visually inspect the updated packages.
  > git diff devops/docker_build/poetry.lock

  # Run entire release process.
  > i docker_release_dev_image
  ```

  ## Experiment in a local image

- To install packages in an image, do `i docker_bash`

  ```bash
  # Switch to root and install package.
  > sudo su -
  > source /venv/bin/activate
  > pip install <package>

  # Switch back to user.
  > exit
  ```

- You should test that the package is installed for your user, e.g.,
  ```bash
  > source /venv/bin/activate python -c "import foobar; print(foobar);print(foobar.__version__)"
  ```
- You can now use the package in this container. Note that if you exit the
  container, the modified image is lost, so you need to install it again.
- You can save the modified image, tagging the new image as local, while the
  container is still running.
- Copy your Container ID. You can find it
  - In the docker bash session, e.g., if the command line in the container
    starts with `user_1011@da8f3bb8f53b:/app$`, your Container ID is
    `da8f3bb8f53b`
  - By listing running containers, e.g., run `docker ps` outside the container
- Commit image
  ```bash
  > docker commit <Container ID> <IMAGE>/cmamp:local-$USER
  ```
  - E.g.
    `docker commit da8f3bb8f53b 665840871993.dkr.ecr.us-east-1.amazonaws.com/cmamp:local-julias`
- If you are running inside a notebook using `i docker_jupyter` you can install
  packages using a one liner `! sudo su -; source ...; `

## Github Actions (CI)

- To run a single test in GH Action
  - Create a branch
  - Change .github/workflows/fast_tests.yml
    ```bash
    run: invoke run_fast_tests
    --pytest-opts="helpers/test/test_git.py::Test_git_modified_files1::test_get_modified_files_in_branch1
    -s --dbg"
    ```

## Pytest

- From
  [https://gist.github.com/kwmiebach/3fd49612ef7a52b5ce3a](https://gist.github.com/kwmiebach/3fd49612ef7a52b5ce3a)

- More details on running unit tests with `invoke` is
  [/docs/coding/all.run_unit_tests.how_to_guide.md](/docs/coding/all.run_unit_tests.how_to_guide.md)

### Run with Coverage

```bash
> i run_fast_tests --pytest-opts="core/test/test_finance.py" --coverage
```

### Capture Output of a Pytest

- Inside the `dev` container (i.e., docker bash)

  ```bash
  docker> pytest_log ...
  ```
  - This captures the output in a file `tmp.pytest_script.txt`

- Get the failed tests (inside or outside the container)
  ```bash
  [docker]> i pytest_failed
  dataflow/model/test/test_run_notebooks.py::Test_run_master_research_backtest_analyzer::test_run_notebook1
  dataflow/system/test/test_real_time_runner.py::TestRealTimeDagRunner1::test_simulated_replayed_time1
  dataflow/model/test/test_dataframe_modeler.py::TestDataFrameModeler::test_dump_json1
  ...
  ```

### Run Only One Test Based on Its Name

- Outside the `dev` container

  ```bash
  > i find_test_class Test_obj_to_str1
  INFO: > cmd='/Users/saggese/src/venv/amp.client_venv/bin/invoke find_test_class Test_obj_to_str1'
  ## find_test_class: class_name abs_dir pbcopy
  10:18:42 - INFO  lib_tasks_find.py _find_test_files:44                  Searching from '.'

  # Copied to system clipboard:
  ./helpers/test/test_hobject.py::Test_obj_to_str1
  ```

### Iterate on Stacktrace of Failing Test

- Inside docker bash
  ```bash
  docker> pytest ...
  ```
- The test fails: switch to using `pytest_log` to save the stacktrace to a file

  ```bash
  > pytest_log dataflow/model/test/test_tiled_flows.py::Test_evaluate_weighted_forecasts::test_combine_two_signals
  ...
  =================================== FAILURES ===================================
  __________ Test_evaluate_weighted_forecasts.test_combine_two_signals ___________
  Traceback (most recent call last):
    File "/app/dataflow/model/test/test_tiled_flows.py", line 78, in test_combine_two_signals
      bar_metrics = dtfmotiflo.evaluate_weighted_forecasts(
    File "/app/dataflow/model/tiled_flows.py", line 265, in evaluate_weighted_forecasts
      weighted_sum = hpandas.compute_weighted_sum(
  TypeError: compute_weighted_sum() got an unexpected keyword argument 'index_mode'
  ============================= slowest 3 durations ==============================
  2.18s call     dataflow/model/test/test_tiled_flows.py::Test_evaluate_weighted_forecasts::test_combine_two_signals
  0.01s setup    dataflow/model/test/test_tiled_flows.py::Test_evaluate_weighted_forecasts::test_combine_two_signals
  0.00s teardown dataflow/model/test/test_tiled_flows.py::Test_evaluate_weighted_forecasts::test_combine_two_signals
  ```

- Then from outside `dev` container launch `vim` in quickfix mode

  ```bash
  > invoke traceback
  ```

- The short form is `it`

### Iterating on a Failing Regression Test

- The workflow is:

  ```bash
  # Run a lot of tests, e.g., the entire regression suite.
  > pytest ...
  # Some tests fail.

  # Run the `pytest_repro` to summarize test failures and to generate commands to reproduce them.
  > invoke pytest_repro
  ```

### Detect Mismatches with Golden Test Outcomes

- The command is

  ```bash
  > i pytest_find_unused_goldens
  ```

- The specific dir to check can be specified with the `dir_name` parameter.
- The invoke detects and logs mismatches between the tests and the golden
  outcome files.
  - When goldens are required by the tests but the corresponding files do not
    exist
    - This usually happens if the tests are skipped or commented out.
    - Sometimes it's a FP hit (e.g. the method doesn't actually call
      `check_string` but instead has it in a string, or `check_string` is called
      on a missing file on purpose to verify that an exception is raised).
  - When the existing golden files are not actually required by the
    corresponding tests.
    - In most cases it means the files are outdated and can be deleted.
    - Alternatively, it can be a FN hit: the test method A, which the golden
      outcome corresponds to, doesn't call `check_string` directly, but the
      test's class inherits from a different class, which in turn has a method B
      that calls `check_string`, and this method B is called in the test method
      A.
- For more details see
  [CmTask528](https://github.com/cryptokaizen/cmamp/issues/528).

## Lint

### Lint Everything

```bash
> i lint --phases="amp_isort amp_class_method_order amp_normalize_import
amp_format_separating_line amp_black" --files='$(find . -name "\*.py")'
```
