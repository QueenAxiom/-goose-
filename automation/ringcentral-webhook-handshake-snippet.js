/**
 * Paste into a Code node placed immediately after the Webhook node in the
 * EXISTING receive-handler workflow, before any SMS-processing logic.
 *
 * Why this exists: RingCentral's subscription-creation call (see
 * automation/ringcentral-subscription-register.json) makes an immediate
 * validation request to the webhook URL carrying a `Validation-Token`
 * header. If that header isn't echoed straight back, the create/renew call
 * fails and the whole system never receives a message. This must be live
 * BEFORE the registration workflow is ever run against production.
 *
 * Mode: "Run Once for All Items". Requires the Webhook node's "Respond"
 * setting to be "Using Respond to Webhook Node" so this can short-circuit
 * the response for handshake requests.
 */

const items = $input.all();
const headers = items[0].json.headers || {};
const validationToken = headers['validation-token'] || headers['Validation-Token'];

if (validationToken) {
  // RingCentral handshake — echo the token back, empty body, stop here.
  // Wire this item to a "Respond to Webhook" node configured with:
  //   Response Code: 200
  //   Response Headers: Validation-Token = {{ $json.validationToken }}
  //   Response Body: (empty)
  return [
    {
      json: {
        isHandshake: true,
        validationToken,
      },
    },
  ];
}

// Not a handshake — real SMS event, fall through to existing processing.
return [
  {
    json: {
      ...items[0].json,
      isHandshake: false,
    },
  },
];
