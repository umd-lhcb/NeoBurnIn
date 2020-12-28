{ stdenv
, buildPythonPackage
, aiohttp
, aiohttp-cors
, aiojobs
, janus
, rainbow_logging_handler
, pyyaml
, curses-menu
, rpi_burnin
, labSNMP
}:

buildPythonPackage rec {
  pname = "NeoBurnIn";
  version = "0.5.4";

  src = builtins.path { path = ./..; name = pname; };

  propagatedBuildInputs = [
    aiohttp
    aiohttp-cors
    aiojobs
    janus
    rainbow_logging_handler
    pyyaml
    curses-menu
    rpi_burnin
    labSNMP
  ];

  doCheck = false;
}
