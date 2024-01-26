{ stdenv, makeWrapper, writeScriptBin, python3, git, jq, betterfox-extractor, ... }:
let
  script = writeScriptBin "betterfox-generator" ''
    #!${python3}/bin/python

    ${builtins.readFile ./generator.py}
  '';
in
stdenv.mkDerivation {
  pname = "betterfox-generator";
  version = "1.0";
  src = script;
  buildInputs = [ python3 makeWrapper git jq betterfox-extractor ];
  installPhase = ''
    mkdir -p $out/bin
    cp $src/bin/betterfox-generator $out/bin
    wrapProgram $out/bin/betterfox-generator \
      --prefix PATH : ${git}/bin \
      --prefix PATH : ${jq}/bin \
      --prefix PATH : ${betterfox-extractor}/bin
  '';
}
