{ stdenv, buildPythonPackage, fetchPypi, aiohttp }:

buildPythonPackage rec {
  pname = "aiojobs";
  version = "0.2.2";

  src = fetchPypi {
    inherit pname version;
    extension = "tar.gz";
    sha256 = "8e4b3e3d1bdb970bdaf8f8cd5eb4e4ff3e0e01a4abd22b4f73a87002a5ae4005";
  };

  propagatedBuildInputs = [
    aiohttp
  ];

  doCheck = false;
}
