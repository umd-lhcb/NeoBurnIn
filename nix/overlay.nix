final: prev:
let
  pythonOverrides = {
    packageOverrides = self: super: {
      rainbow_logging_handler = super.callPackage ./rainbow_logging_handler { };
      aiojobs = super.callPackage ./aiojobs { };
      janus = super.callPackage ./janus { };
      curses-menu = super.callPackage ./curses-menu { };
    };
  };
in
rec {
  python3 = prev.python3.override pythonOverrides;
}
