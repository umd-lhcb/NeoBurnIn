{ stdenv, buildPythonPackage, fetchgit, RPi_GPIO, fake_rpi, hidapi }:

buildPythonPackage rec {
  pname = "rpi.burnin";
  version = "0.3.2";

  src = fetchgit {
    url = "https://github.com/umd-lhcb/${pname}";
    rev = version;
    sha256 = "0dksvff3md9j2rzmg1d8x7hmq21swkj1cy080q74nahz68wqmmh2";
  };

  propagatedBuildInputs = [ hidapi ]
  ++ stdenv.lib.optionals (stdenv.isDarwin) [ fake_rpi ]
  ++ stdenv.lib.optionals (!stdenv.isDarwin) [ RPi_GPIO ]
  ;

  # No check avaliable
  doCheck = false;
}
