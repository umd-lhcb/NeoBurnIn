{ stdenv, buildPythonPackage, fetchPypi
, colorama, logutils }:

buildPythonPackage rec {
  pname = "rainbow_logging_handler";
  version = "2.2.2";

  src = fetchPypi {
    inherit pname version;
    extension = "zip";
    sha256 = "a504c20f1e074cc7f5a5b986c08eb6fb495c9153cffb36b5fa0a587de3a8db63";
  };

  propagatedBuildInputs = [
    colorama
    logutils
  ];

  # No check avaliable
  doCheck = false;
}
