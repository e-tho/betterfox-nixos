{ stdenv, writeScriptBin, python3, git, jq, betterfoxExtractor, ... }:
let
  script = writeScriptBin "betterfox-generator" ''
    #!${python3}/bin/python

    ${builtins.readFile ./betterfox-generator.py}
  '';
in
stdenv.mkDerivation {
  pname = "betterfox-generator";
  version = "1.0";
  src = script;
  buildInputs = [ python3 makeWrapper git jq betterfoxExtractor ];
  installPhase = ''
    mkdir -p $out/bin
    cp $src/bin/betterfox-generator $out/bin
    wrapProgram $out/bin/betterfox-generator \
      --prefix PATH : ${git}/bin \
      --prefix PATH : ${jq}/bin \
      --prefix PATH : ${betterfoxExtractor}/bin
  '';
}
