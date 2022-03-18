pylint --load-plugins pylint_django --fail-under=0 --django-settings-module=backend.settings backend rms ums rdts
coverage run --source backend,ums,rms,rdts -m pytest --junit-xml=xunit-reports/xunit-result.xml
coverage xml -o coverage-reports/coverage.xml
coverage report
