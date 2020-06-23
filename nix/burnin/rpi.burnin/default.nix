{ stdenv, buildPythonPackage, fetchgit, RPi_GPIO, fake_rpi, hidapi }:

buildPythonPackage rec {
  pname = "rpi.burnin";
  version = "0.3.2";

  src = fetchgit {
    url = "https://github.com/umd-lhcb/${pname}";
    rev = version;
    sha256 = "17b6wvq4v7wlz2dkh8g49q8q2smq5gysirhklyah0jcl443wmk6x";
  };

  propagatedBuildInputs = [ hidapi ]
  ++ stdenv.lib.optionals (stdenv.isDarwin) [ fake_rpi ]
  ++ stdenv.lib.optionals (!stdenv.isDarwin) [ RPi_GPIO ]
  ;

  # No check avaliable
  doCheck = false;
}
