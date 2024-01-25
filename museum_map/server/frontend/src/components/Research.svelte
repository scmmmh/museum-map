<script lang="ts">
  import { onDestroy, tick } from "svelte";

  import ResearchConsent from "./ResearchConsent.svelte";
  import { localPreferences, consent, trackingAllowed } from "../store";

  // Dialog defaults to visible, if the dialog has never been shown before
  let dialogVisible = !$localPreferences || !$localPreferences.tracking;
  let dialogHeader: HTMLElement | null = null;
  let researchButton: HTMLButtonElement | null = null;

  if (dialogVisible) {
    tick().then(() => {
      if (dialogHeader) {
        dialogHeader.focus();
      }
    });
  }

  function toggleDialog() {
    if (dialogVisible) {
      dialogVisible = false;
      if (researchButton) {
        researchButton.focus();
      }
    } else {
      dialogVisible = true;
      tick().then(() => {
        if (dialogHeader) {
          dialogHeader.focus();
        }
      });
    }
  }

  function keyboardListener(ev: KeyboardEvent) {
    if (ev.key === "Escape") {
      if (dialogVisible) {
        dialogVisible = false;
        if (researchButton) {
          researchButton.focus();
        }
      }
    }
  }

  const consentUnsubscribe = consent.subscribe((consent) => {
    if (
      $localPreferences !== undefined &&
      $localPreferences.tracking !== undefined &&
      $localPreferences.tracking !== null
    ) {
      if (dialogVisible) {
        dialogVisible = false;
        if (researchButton) {
          researchButton.focus();
        }
      }
    }
  });

  onDestroy(consentUnsubscribe);
</script>

<svelte:document on:keyup={keyboardListener} />

<div class="fixed left-0 bottom-0 ml-2 mb-2">
  <button
    bind:this={researchButton}
    on:click={toggleDialog}
    aria-label="Contribute to our research"
    class="relative block p-2 text-white bg-blue-800 rounded-lg"
  >
    <svg
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      class="w-8 h-8 md:w-12 md:h-12"
      fill="currentColor"
      aria-hidden="true"
      ><title>Contribute to our research</title><path
        d="M5,19A1,1 0 0,0 6,20H18A1,1 0 0,0 19,19C19,18.79 18.93,18.59 18.82,18.43L13,8.35V4H11V8.35L5.18,18.43C5.07,18.59 5,18.79 5,19M6,22A3,3 0 0,1 3,19C3,18.4 3.18,17.84 3.5,17.37L9,7.81V6A1,1 0 0,1 8,5V4A2,2 0 0,1 10,2H14A2,2 0 0,1 16,4V5A1,1 0 0,1 15,6V7.81L20.5,17.37C20.82,17.84 21,18.4 21,19A3,3 0 0,1 18,22H6M13,16L14.34,14.66L16.27,18H7.73L10.39,13.39L13,16M12.5,12A0.5,0.5 0 0,1 13,12.5A0.5,0.5 0 0,1 12.5,13A0.5,0.5 0 0,1 12,12.5A0.5,0.5 0 0,1 12.5,12Z"
      /></svg
    >
    {#if $trackingAllowed}
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        class="absolute right-0 bottom-0 p-1 w-6 h-6 bg-blue-800"
        fill="currentColor"
        aria-label="You have enabled tracking to support our research"
        ><title>shoe-print</title><path
          d="M10.74,11.72C11.21,12.95 11.16,14.23 9.75,14.74C6.85,15.81 6.2,13 6.16,12.86L10.74,11.72M5.71,10.91L10.03,9.84C9.84,8.79 10.13,7.74 10.13,6.5C10.13,4.82 8.8,1.53 6.68,2.06C4.26,2.66 3.91,5.35 4,6.65C4.12,7.95 5.64,10.73 5.71,10.91M17.85,19.85C17.82,20 17.16,22.8 14.26,21.74C12.86,21.22 12.8,19.94 13.27,18.71L17.85,19.85M20,13.65C20.1,12.35 19.76,9.65 17.33,9.05C15.22,8.5 13.89,11.81 13.89,13.5C13.89,14.73 14.17,15.78 14,16.83L18.3,17.9C18.38,17.72 19.89,14.94 20,13.65Z"
        /></svg
      >
    {/if}
  </button>
</div>

{#if dialogVisible}
  <div
    class="fixed left-0 md:left-1/2 bottom-0 w-screen xl:w-9/12 max-h-1/2 lg:max-h-none md:transform md:-translate-x-1/2 flex flex-col z-40 p-4 bg-neutral-700 text-white shadow-even shadow-black"
  >
    <h2
      bind:this={dialogHeader}
      class="text-xl font-bold mb-4 order-1"
      tabindex="-1"
    >
      Participate in our Research
    </h2>
    <ResearchConsent />
    <button
      class="absolute right-0 top-0 transform -translate-x-1 xl:translate-x-1/2 -translate-y-1/2 bg-blue-800 text-white rounded-full"
      aria-label="Close this dialog"
      on:click={toggleDialog}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24"
        class="w-10 h-10 p-2 md:w-8 md:h-8 md:p-1"
        fill="currentColor"
        ><title>Close this dialog</title><path
          d="M12,20C7.59,20 4,16.41 4,12C4,7.59 7.59,4 12,4C16.41,4 20,7.59 20,12C20,16.41 16.41,20 12,20M12,2C6.47,2 2,6.47 2,12C2,17.53 6.47,22 12,22C17.53,22 22,17.53 22,12C22,6.47 17.53,2 12,2M14.59,8L12,10.59L9.41,8L8,9.41L10.59,12L8,14.59L9.41,16L12,13.41L14.59,16L16,14.59L13.41,12L16,9.41L14.59,8Z"
        /></svg
      >
    </button>
  </div>
{/if}
