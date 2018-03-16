import testinfra.utils.ansible_runner
import pytest

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    '.molecule/ansible_inventory').get_hosts('all')


def test_service_running_and_enabled(Command, Service, File):
    if File('/etc/redhat-release').exists:
        service = Service('haproxy')
        assert service.is_running
        assert service.is_enabled
    else:
        # BUG: testinfra tries to use systemd
        out = Command.check_output('service haproxy status')
        assert out == 'haproxy is running.'


@pytest.mark.parametrize('name', [
    'haproxy.log',
    'haproxy-http.log',
    'haproxy-tcp.log',
])
def test_logfiles(File, Sudo, name):
    with Sudo():
        assert File('/var/log/haproxy/%s' % name).exists


def test_http(Command, File, Sudo):
    out = Command.check_output("curl -s http://localhost/")
    assert '503 Service Unavailable' in out
    assert 'No server is available to handle this request.' in out
    with Sudo():
        log = File('/var/log/haproxy/haproxy-http.log')
        assert log.content_string.splitlines()[-1].endswith(
            '0/0/0/0/0 0/0 "GET / HTTP/1.1"')


def test_tcp(Command, File, Sudo):
    out = Command.check_output("curl -s http://localhost:81/")
    assert '503 Service Unavailable' in out
    assert 'No server is available to handle this request.' in out
    with Sudo():
        log = File('/var/log/haproxy/haproxy-tcp.log')
        assert log.content_string.splitlines()[-1].endswith(
            '0/0/0/0/0 0/0')
