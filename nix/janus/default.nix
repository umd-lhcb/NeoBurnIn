{ lib, buildPythonPackage, fetchPypi, pytestCheckHook, pythonOlder, pytest-asyncio }:

buildPythonPackage rec {
  pname = "janus";
  version = "0.4.0";

  src = fetchPypi {
    inherit pname version;
    sha256 = "cfc221683160b91b35bae1917e2957b78dad10a2e634f4f8ed119ed72e2a88ef";
  };

  disabled = pythonOlder "3.6";

  checkInputs = [ pytest-asyncio pytestCheckHook ];

  # also fails upstream: https://github.com/aio-libs/janus/pull/258
  disabledTests = [ "test_format" ];

  meta = with lib; {
    description = "Mixed sync-async queue";
    homepage = "https://github.com/aio-libs/janus";
    license = licenses.asl20;
    maintainers = [ maintainers.simonchatts ];
  };
}
