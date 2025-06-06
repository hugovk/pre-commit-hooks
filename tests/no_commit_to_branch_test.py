from __future__ import annotations

import pytest

from pre_commit_hooks.no_commit_to_branch import is_on_branch
from pre_commit_hooks.no_commit_to_branch import main
from pre_commit_hooks.util import cmd_output
from testing.util import git_commit


def test_other_branch(temp_git_dir):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', 'anotherbranch')
        assert is_on_branch({'placeholder'}) is False


def test_multi_branch(temp_git_dir):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', 'another/branch')
        assert is_on_branch({'placeholder'}) is False


def test_multi_branch_fail(temp_git_dir):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', 'another/branch')
        assert is_on_branch({'another/branch'}) is True


def test_exact_branch(temp_git_dir):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', 'branchname')
        assert is_on_branch({'branchname'}) is True


def test_main_branch_call(temp_git_dir):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', 'other')
        assert main(('--branch', 'other')) == 1


@pytest.mark.parametrize('branch_name', ('b1', 'b2'))
def test_forbid_multiple_branches(temp_git_dir, branch_name):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', branch_name)
        assert main(('--branch', 'b1', '--branch', 'b2'))


def test_branch_pattern_fail(temp_git_dir):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', 'another/branch')
        assert is_on_branch(set(), {'another/.*'}) is True


@pytest.mark.parametrize('branch_name', ('somebranch', 'another/branch'))
def test_branch_pattern_multiple_branches_fail(temp_git_dir, branch_name):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', branch_name)
        assert main(('--branch', 'somebranch', '--pattern', 'another/.*'))


def test_main_default_call(temp_git_dir):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', 'anotherbranch')
        assert main(()) == 0


def test_not_on_a_branch(temp_git_dir):
    with temp_git_dir.as_cwd():
        git_commit('--allow-empty', '-m1')
        head = cmd_output('git', 'rev-parse', 'HEAD').strip()
        cmd_output('git', 'checkout', head)
        # we're not on a branch!
        assert main(()) == 0


@pytest.mark.parametrize('branch_name', ('master', 'main'))
def test_default_branch_names(temp_git_dir, branch_name):
    with temp_git_dir.as_cwd():
        cmd_output('git', 'checkout', '-b', branch_name)
        assert main(()) == 1
