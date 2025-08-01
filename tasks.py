import logging
import os
from typing import Any

import helpers.repo_config_utils as hrecouti

# Expose the pytest targets.
# Extract with:
# > i print_tasks --as-code
from helpers.lib_tasks import (  # This is not an invoke target.
    parse_command_line,
    set_default_params,
)

# TODO(gp): Remove the lib_tasks import and import directly from lib_tasks_*.py files.
# TODO(gp): How to automatically discovery the paths?

from helpers.lib_tasks import (  # isort: skip # noqa: F401  # pylint: disable=unused-import
    aws_create_test_task_definition,
    aws_create_prod_task_definition,
    docker_release_test_task_definition,
    docker_release_prod_task_definition,
    docker_bash,
    docker_build_local_image,
    docker_build_multi_arch_prod_image,
    docker_build_prod_image,
    docker_cmd,
    docker_create_candidate_image,
    # docker_dash_app,
    docker_images_ls_repo,
    docker_jupyter,
    docker_kill,
    docker_login,
    docker_ps,
    docker_pull,
    docker_pull_helpers,
    docker_push_dev_image,
    docker_push_prod_candidate_image,
    docker_push_prod_image,
    docker_release_dev_image,
    docker_release_prod_image,
    docker_rollback_dev_image,  # TODO(gp): -> docker_release_rollback_dev_image
    docker_rollback_prod_image,
    docker_stats,
    docker_tag_local_image_as_dev,  # TODO(gp): -> docker_release_...
    docker_tag_push_multi_arch_prod_image,
    docker_update_prod_task_definition,
    #
    bash_print_path,
    bash_print_tree,
    #
    find,
    find_check_string_output,
    find_dependency,
    find_test_class,
    find_test_decorator,
    fix_perms,
    gh_create_pr,
    gh_issue_title,
    gh_login,
    gh_workflow_list,
    gh_workflow_run,
    git_add_all_untracked,
    git_branch_copy,
    git_branch_create,
    git_branch_delete_merged,
    git_branch_diff_with,
    git_branch_files,
    git_branch_next_name,
    git_branch_rename,
    git_clean,
    git_fetch_master,
    git_files,
    git_last_commit_files,
    git_merge_master,
    git_patch_create,
    git_pull,
    git_repo_copy,
    git_roll_amp_forward,
    integrate_create_branch,
    integrate_diff_dirs,
    integrate_diff_overlapping_files,
    integrate_files,
    integrate_find_files,
    integrate_find_files_touched_since_last_integration,
    integrate_rsync,
    lint,
    lint_check_python_files,
    lint_check_python_files_in_docker,
    lint_create_branch,
    lint_detect_cycles,
    lint_sync_code,
    print_env,
    print_setup,
    print_tasks,
    pytest_add_untracked_golden_outcomes,
    pytest_buildmeister,
    pytest_buildmeister_check,
    pytest_clean,
    pytest_collect_only,
    pytest_compare_logs,
    pytest_failed,
    pytest_find_unused_goldens,
    pytest_rename_test,
    pytest_repro,
    run_blank_tests,
    run_coverage_report,
    run_coverage,
    run_coverage_subprocess,
    run_fast_slow_superslow_tests,
    run_fast_slow_tests,
    run_fast_tests,
    run_qa_tests,
    run_slow_tests,
    run_superslow_tests,
    run_tests,
    traceback,
)

# A lib contains dependencies that exist only in a Docker environment. Skipping the import
# if needed in order not to break other invoke targets.
try:
    from oms.lib_tasks_binance import (  # isort: skip # noqa: F401  # pylint: disable=unused-import
        binance_display_open_positions,
        binance_flatten_account,
        binance_log_open_positions,
        binance_log_total_balance,
    )
except ImportError:
    pass
# Collect imports that fails due to the `helpers` image is not being updated. See CmTask4892 for details.
try:
    from helpers.lib_tasks import (  # isort: skip # noqa: F401  # pylint: disable=unused-import
        copy_ecs_task_definition_image_url,
        docker_release_multi_build_dev_image,
        docker_release_multi_arch_prod_image,
        docker_tag_push_multi_build_local_image_as_dev,
        release_dags_to_airflow,
        integrate_file,
        lint_check_if_it_was_run,
    )
except ImportError:
    pass
try:
    from helpers.lib_tasks_gh import (  # isort: skip # noqa: F401  # pylint: disable=unused-import
        gh_publish_buildmeister_dashboard_to_s3,
    )
except ImportError:
    pass
# # TODO(gp): This is due to the coupling between code in linter container and
# #  the code being linted.
# try:
#     from helpers.lib_tasks import (  # isort: skip # noqa: F401  # pylint: disable=unused-import
#         docker_update_prod_task_definition,
#     )
# except ImportError as e:
#     #print(e)
#     pass


_LOG = logging.getLogger(__name__)


# #############################################################################
# Setup.
# #############################################################################


# TODO(gp): Move it to lib_tasks.
ECR_BASE_PATH = os.environ["CSFY_ECR_BASE_PATH"]


def _run_qa_tests(ctx: Any, stage: str, version: str) -> bool:
    """
    Run QA tests to verify that the invoke tasks are working properly.

    This is used when qualifying a docker image before releasing.
    """
    _ = ctx
    # The QA tests are in `qa_test_dir` and are marked with `qa_test_tag`.
    qa_test_dir = "test"
    # qa_test_dir = "test/test_tasks.py::TestExecuteTasks1::test_docker_bash"
    qa_test_tag = "qa and not superslow"
    cmd = f'pytest -m "{qa_test_tag}" {qa_test_dir} --image_stage {stage}'
    if version:
        cmd = f"{cmd} --image_version {version}"
    ctx.run(cmd)
    return True


default_params = {
    # TODO(Nikola): Remove prefix after everything is cleaned.
    #   Currently there are a lot dependencies on prefix.
    "CSFY_ECR_BASE_PATH": ECR_BASE_PATH,
    # When testing a change to the build system in a branch you can use a different
    # image, e.g., `XYZ_tmp` to not interfere with the prod system.
    # "BASE_IMAGE": "amp_tmp",
    "BASE_IMAGE": hrecouti.get_repo_config().get_docker_base_image_name(),
    "QA_TEST_FUNCTION": _run_qa_tests,
}


set_default_params(default_params)
parse_command_line()
