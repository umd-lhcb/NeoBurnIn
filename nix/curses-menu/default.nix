{ stdenv, buildPythonPackage, fetchPypi }:

buildPythonPackage rec {
  pname = "curses-menu";
  version = "0.5.0";

  patches = [ ./no_dep.patch ];

  src = fetchPypi {
    inherit pname version;
    extension = "zip";
    sha256 = "29c45e2f16283833e2940fac0fd64e948f2ff603d3e11f510c5bd2b946cd8981";
  };

  doCheck = false;
}
