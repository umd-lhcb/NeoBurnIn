self: super:

let
  pythonOverrides = {
    packageOverrides = self: super: {
      build_utils = super.callPackage ./build_utils {};
      RPi_GPIO = super.callPackage ./RPi.GPIO {};
      fake_rpi = super.callPackage ./fake_rpi {};
      rpi_burnin = super.callPackage ./rpi.burnin {};
      labSNMP = super.callPackage ./labSNMP {};
      rainbow_logging_handler = super.callPackage ./rainbow_logging_handler {};
      aiojobs = super.callPackage ./aiojobs {};
    };
  };
in

{
  python3 = super.python3.override pythonOverrides;
}
