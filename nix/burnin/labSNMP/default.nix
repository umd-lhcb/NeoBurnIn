{ stdenv, buildPythonPackage, fetchgit, pysnmp }:

buildPythonPackage rec {
  pname = "labSNMP";
  version = "0.2";

  src = fetchgit {
    url = "https://github.com/umd-lhcb/${pname}";
    rev = version;
    sha256 = "0p39q43dxbnx9fqzy7v63xz29gvypya7216l03xmlbd8rmwpwni1";
  };

  propagatedBuildInputs = [ pysnmp ];

  # No check avaliable
  doCheck = false;
}
