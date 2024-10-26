# Extender Ontología a GO
Observar este ejemplo para extender el modelo a la ontologia de genes.

MONDO-Gene relationship
MONDO_0011518 Wiedemann-Steiner syndrome
RO_0004003 has material basis in germline mutation in 
http://identifiers.org/hgnc/7132 KMT2A

```json
{
      "sub" : "http://purl.obolibrary.org/obo/MONDO_0011518",
      "pred" : "http://purl.obolibrary.org/obo/RO_0004003",
      "obj" : "http://identifiers.org/hgnc/7132",
      "meta" : {
        "basicPropertyValues" : [ {
          "pred" : "http://www.geneontology.org/formats/oboInOwl#source",
          "val" : "MONDO:mim2gene_medgen"
        } ]
      }
    }
```