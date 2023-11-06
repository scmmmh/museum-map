/// <reference types="svelte" />
/// <reference types="vite/client" />

type APIStatus = {
  ready: boolean,
  version: string,
}
type LogAction = {
  action: string,
  params: object,
};
