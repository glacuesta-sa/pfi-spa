import { type ClientSchema, a, defineData } from "@aws-amplify/backend";

const schema = a.schema({
  DendogramNode: a
    .model({
      id: a.integer(),
      childLabel: a.string(),
      parentId: a.integer(),
    })
    .authorization((allow) => [allow.publicApiKey()]),
});

export type Schema = ClientSchema<typeof schema>;

export const data = defineData({
  schema,
  authorizationModes: {
    defaultAuthorizationMode: "apiKey",
    // API Key is used for a.allow.public() rules
    apiKeyAuthorizationMode: {
      expiresInDays: 30,
    },
  },
});

