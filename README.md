# Z80 Instruction List

The main file in this repository is `insts.json`, which contains JSON encoded descriptions for the encodings of the Z80 instruction set. The file is generated in the `src` directory from [Zilog's user manual](https://www.zilog.com/docs/z80/um0080.pdf).

## Schema

Note that the page number is the page number you would navigate to in a PDF viewer, not the number printed on the page. Note also that each subarray of `encoding` represents one byte. For the meaning of the non `[01]+` values in `encoding`, see page 53 in the manual.

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Z80 Instruction List",
  "description": "A list of Z80 instructions",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "page": {
        "type": "number"
      },
      "inst": {
        "type": "string"
      },
      "op_code": {
        "type": "string"
      },
      "operands": {
        "type": "array",
        "items": {
          "enum": [
            "(BC)",
            "(C)",
            "(DE)",
            "(HL)",
            "(IX)",
            "(IX+d)",
            "(IY)",
            "(IY+d)",
            "(SP)",
            "(n)",
            "(nn)",
            "0",
            "1",
            "2",
            "A",
            "AF",
            "AF'",
            "C",
            "DE",
            "HL",
            "I",
            "IX",
            "IY",
            "NC",
            "NZ",
            "R",
            "SP",
            "Z",
            "b",
            "cc",
            "dd",
            "e",
            "n",
            "nn",
            "p",
            "pp",
            "qq",
            "r",
            "r'",
            "r*",
            "rn",
            "rr",
            "ss"
          ]
        }
      },
      "encoding": {
        "type": "array",
        "items": {
          "type": "array",
          "items": {
            "oneOf": [
              {
                "type": "string",
                "description": "A binary string",
                "pattern": "^[01]+$"
              },
              {
                "type": "string",
                "description": "A single register, assembled as give on pp. 85",
                "pattern": "^r[*']?$"
              },
              {
                "description": "Encoded form of input for RST instruction, se pp. 306",
                "const": "t"
              },
              {
                "description": "A one-byte signed integer expression",
                "const": "d"
              },
              {
                "description": "A one-bit integer expression, assembled as given on pp. 257",
                "const": "b"
              },
              {
                "description": "A one-byte integer expression representing the relative jump, see pp. 265",
                "const": "e-2"
              },
              {
                "description": "A one-byte unsigned integer expression",
                "const": "n"
              },
              {
                "description": "A register pair from BC, DE, HL, AF, assembled as given on pp. 129",
                "const": "qq"
              },
              {
                "description": "A register pair from BC, DE, HL, SP, assembled as given on pp. 202",
                "const": "ss"
              },
              {
                "description": "A register pair from BC, DE, IX, SP, assembled as given on pp. 208",
                "const": "pp"
              },
              {
                "description": "A register pair from BC, DE, IY, SP, assembled as given on pp. 210",
                "const": "rr"
              },
              {
                "description": "Status of the flags register, assembled as given on pp. 277.",
                "const": "cc"
              }
            ]
          }
        }
      }
    }
  }
}
```
