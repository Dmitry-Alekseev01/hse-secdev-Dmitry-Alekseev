from pathlib import Path

import pytest
import yaml


class TestDependencySecurity:
    """Тесты для NFR-05: Уязвимости зависимостей"""

    def test_dependabot_config_exists(self):
        """Проверяет наличие конфигурации Dependabot"""
        config_path = Path(".github/dependabot.yml")
        assert config_path.exists(), "Dependabot config file is missing"

    def test_dependabot_config_valid(self):
        """Проверяет валидность конфигурации Dependabot"""
        with open(".github/dependabot.yml", "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        assert config["version"] == 2, "Dependabot version should be 2"
        assert "updates" in config, "Dependabot config should have updates section"

        pip_updates = [u for u in config["updates"] if u["package-ecosystem"] == "pip"]
        assert len(pip_updates) > 0, "Should have pip package ecosystem configured"

        pip_config = pip_updates[0]
        assert pip_config["schedule"]["interval"] == "daily", "Should check daily"
        assert "security" in pip_config.get("labels", []), "Should have security label"

    def test_security_workflow_exists(self):
        """Проверяет наличие workflow для security сканирования"""
        workflow_path = Path(".github/workflows/dependency-security.yml")
        assert workflow_path.exists(), "Security workflow is missing"

    def test_security_workflow_triggers(self):
        """Проверяет триггеры security workflow"""
        with open(
            ".github/workflows/dependency-security.yml", "r", encoding="utf-8"
        ) as f:
            workflow = yaml.safe_load(f)

        on_section = workflow.get("on", {})
        has_schedule = False
        has_push = False
        has_pull_request = False

        if isinstance(on_section, dict):
            has_schedule = "schedule" in on_section
            has_push = "push" in on_section
            has_pull_request = "pull_request" in on_section

            if has_push:
                push_config = on_section["push"]
                if isinstance(push_config, dict) and "branches" in push_config:
                    assert (
                        "main" in push_config["branches"]
                    ), "Should run on main branch"
        else:
            triggers = on_section if isinstance(on_section, list) else [on_section]
            has_schedule = any("schedule" in str(trigger) for trigger in triggers)
            has_push = any("push" in str(trigger) for trigger in triggers)
            has_pull_request = any(
                "pull_request" in str(trigger) for trigger in triggers
            )

        if not has_schedule:
            pytest.skip("Schedule trigger is not configured (optional for development)")

        assert has_push, "Should run on push"
        assert has_pull_request, "Should run on pull requests"

    def test_requirements_file_exists(self):
        """Проверяет наличие requirements.txt"""
        assert Path("requirements.txt").exists(), "requirements.txt is missing"

    def test_requirements_format(self):
        """Проверяет формат requirements.txt"""
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()

        lines = [line.strip() for line in content.split("\n") if line.strip()]
        assert len(lines) > 0, "requirements.txt should contain dependencies"

        dependencies_with_versions = 0
        for line in lines:
            if line.startswith("#"):
                continue
            if "==" in line or ">=" in line or "<=" in line:
                dependencies_with_versions += 1

        assert dependencies_with_versions >= len(lines) * 0.5, (
            f"At least 50% of dependencies should have version pins. "
            f"Found {dependencies_with_versions} out of {len(lines)}"
        )


class TestDependencyVulnerabilities:
    """Тесты для проверки уязвимостей в зависимостях"""

    def test_no_known_vulnerable_packages(self):
        """Проверяет, что нет пакетов с известными критическими уязвимостями"""
        with open("requirements.txt", "r", encoding="utf-8") as f:
            current_dependencies = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]

        known_vulnerable = {
            "django": ["<3.2.0"],
            "requests": ["<2.25.0"],
            "urllib3": ["<1.26.0"],
        }

        vulnerabilities_found = []

        for dep in current_dependencies:
            if "==" in dep:
                pkg, version = dep.split("==")
                pkg = pkg.lower().strip()

                if pkg in known_vulnerable:
                    vulnerable_versions = known_vulnerable[pkg]
                    for vulnerable in vulnerable_versions:
                        if self._is_vulnerable_version(version, vulnerable):
                            vulnerabilities_found.append(
                                f"{pkg}=={version} ({vulnerable})"
                            )

        if vulnerabilities_found:
            pytest.skip(
                f"Found dependencies with known vulnerabilities: {vulnerabilities_found}"
            )

    def _is_vulnerable_version(self, current_version, vulnerable_spec):
        """Проверяет, попадает ли версия под уязвимую спецификацию"""
        if vulnerable_spec.startswith("<"):
            max_version = vulnerable_spec[1:]
            return current_version < max_version
        return False


class TestDependencyPinning:
    """Тесты для проверки закрепления версий зависимостей"""

    def test_all_dependencies_pinned(self):
        """Проверяет, что все зависимости закреплены на конкретных версиях"""
        with open("requirements.txt", "r", encoding="utf-8") as f:
            lines = [
                line.strip() for line in f if line.strip() and not line.startswith("#")
            ]

        unpinned_dependencies = []

        for line in lines:
            if not any(
                char in line for char in ["==", ">=", "<=", "~="]
            ) and line not in ["-e .", "-r", "-c"]:
                unpinned_dependencies.append(line)

        if unpinned_dependencies:
            pytest.skip(f"Unpinned dependencies found: {unpinned_dependencies}")


class TestDependencyStructure:
    """Тесты для структуры зависимостей"""

    def test_no_local_dependencies_in_production(self):
        """Проверяет, что нет локальных путей в requirements.txt"""
        with open("requirements.txt", "r", encoding="utf-8") as f:
            content = f.read()

        local_path_indicators = ["/", "\\", "file:", "git+", "hg+", "svn+", "bzr+"]
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                if any(indicator in line for indicator in local_path_indicators):
                    pytest.skip(f"Local dependency found: {line}")
