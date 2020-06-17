let
  pkgs = import <nixpkgs> { overlays = [(import ./nix/burnin)]; };
  python = pkgs.python3;
  pythonPackages = python.pkgs;
in

pkgs.mkShell {
  name = "pip-env";
  buildInputs = with pythonPackages; [
    aiohttp
    aiohttp-cors
    janus
    pyyaml
    pysnmp

    rpi_burnin
    rainbow_logging_handler
  ];
}
