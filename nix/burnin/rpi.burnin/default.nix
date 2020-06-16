{ stdenv, buildPythonPackage, fetchgit, RPi_GPIO, hidapi }:

buildPythonPackage rec {
  pname = "rpi.burnin";
  version = "0.3";

  src = fetchgit {
    url = "https://github.com/umd-lhcb/${pname}";
    rev = version;
    sha256 = "13zbrhg1qwmn2q4w0spphvaan4bqfh1g6iq0dmsilnr6g601m7jd";
  };

  propagatedBuildInputs = [
    RPi_GPIO
    hidapi
  ];

  # No check avaliable
  doCheck = false;
}
