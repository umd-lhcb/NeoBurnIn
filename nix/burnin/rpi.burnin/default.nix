{ stdenv, buildPythonPackage, fetchgit, RPi_GPIO, fake_rpi, hidapi }:

buildPythonPackage rec {
  pname = "rpi.burnin";
  version = "0.3.2";

  src = fetchgit {
    url = "https://github.com/umd-lhcb/${pname}";
    rev = version;
    sha256 = "128zqxwd2p4ia4na36i91kj666fn37f6jcgqhr08jf20pnrsvnf8";
  };

  propagatedBuildInputs = [ hidapi ]
  ++ stdenv.lib.optionals (stdenv.isDarwin) [ fake_rpi ]
  ++ stdenv.lib.optionals (!stdenv.isDarwin) [ RPi_GPIO ]
  ;

  # No check avaliable
  doCheck = false;
}
