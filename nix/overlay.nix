final: prev:
let
  pythonOverrides = {
    packageOverrides = self: super: {
      rainbow_logging_handler = super.callPackage ./rainbow_logging_handler { };
      aiojobs = super.callPackage ./aiojobs { };
      janus = super.callPackage ./janus { };
      NeoBurnIn = super.callPackage ./default.nix { };
    };
  };
in
{
  python3 = prev.python3.override pythonOverrides;
  pythonPackages = python3.pkgs;
}
