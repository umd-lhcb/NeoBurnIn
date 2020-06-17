{ stdenv, buildPythonPackage, fetchgit, RPi_GPIO, fake_rpi, hidapi }:

buildPythonPackage rec {
  pname = "rpi.burnin";
  version = "0.3.1";

  src = fetchgit {
    url = "https://github.com/umd-lhcb/${pname}";
    rev = version;
    sha256 = "1771dhib3vfcn4zshc9sgw6m3xnhzrd8pbksgjw6ahac2crxd995";
  };

  propagatedBuildInputs = [ hidapi ]
  ++ stdenv.lib.optionals (stdenv.isDarwin) [ fake_rpi ]
  ++ stdenv.lib.optionals (!stdenv.isDarwin) [ RPi_GPIO ]
  ;

  # No check avaliable
  doCheck = false;
}
