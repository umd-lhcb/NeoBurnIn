let
  pkgs = import <nixpkgs> { overlays = [(import ./nix/burnin)]; };
  python = pkgs.python3;
  pythonPackages = python.pkgs;
in

pkgs.mkShell {
  name = "pip-env";
  buildInputs = with pythonPackages; [
    hidapi

    aiohttp
    aiohttp-cors
    janus
    pyyaml
    pysnmp

    RPi_GPIO
    rainbow_logging_handler
  ];
}
