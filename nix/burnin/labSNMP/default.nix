{ stdenv, buildPythonPackage, fetchgit, pysnmp }:

buildPythonPackage rec {
  pname = "labSNMP";
  version = "0.2";

  src = fetchgit {
    url = "https://github.com/umd-lhcb/${pname}";
    rev = version;
    sha256 = "12346pp8bn6qavab1zz74sggrq3xnyxy3hr4gqmz18ap1jz938as";
  };

  propagatedBuildInputs = [ pysnmp ];

  # No check avaliable
  doCheck = false;
}
