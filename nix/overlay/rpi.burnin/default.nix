{ stdenv, buildPythonPackage, fetchgit, RPi_GPIO, fake_rpi, hidapi }:

buildPythonPackage rec {
  pname = "rpi.burnin";
  version = "0.3.3";

  src = fetchgit {
    url = "https://github.com/umd-lhcb/${pname}";
    rev = version;
    sha256 = "0y82hxypxyrfwnjribzrpl3ll75h34n1wi76kgd3irlirifrx1ka";
  };

  propagatedBuildInputs = [ hidapi ]
  ++ stdenv.lib.optionals (stdenv.isDarwin) [ fake_rpi ]
  ++ stdenv.lib.optionals (!stdenv.isDarwin) [ RPi_GPIO ]
  ;

  # No check avaliable
  doCheck = false;
}
