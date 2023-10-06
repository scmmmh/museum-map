<script lang="ts">
  import { onDestroy, tick } from "svelte";
  import { get } from "svelte/store";
  import { localPreferences, consent, ageBand, tracker } from "../store";

  // Dialog defaults to visible, if the dialog has never been shown before
  let dialogVisible = !$localPreferences || !$localPreferences.tracking;
  let dialogHeader: HTMLElement | null = null;
  let researchButton: HTMLButtonElement | null = null;
  let ageBandSelect: HTMLSelectElement | null = null;
  let thankYouMessage: HTMLElement | null = null;

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

  function setConsent() {
    consent.set(true);
    tick().then(() => {
      if (ageBandSelect) {
        ageBandSelect.focus();
      }
    });
  }

  const consentUnsubscribe = consent.subscribe((consent) => {
    localPreferences.setPreference("tracking.consent", consent);
  });
  const ageBandUnsubscribe = ageBand.subscribe((ageBand) => {
    if (get(tracker)) {
      tick().then(() => {
        if (thankYouMessage) {
          thankYouMessage.focus();
        }
      });
    }
    localPreferences.setPreference("tracking.ageBand", ageBand);
  });

  onDestroy(() => {
    consentUnsubscribe();
    ageBandUnsubscribe();
  });
</script>

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
    {#if $tracker}
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
    class="fixed left-0 md:left-1/2 bottom-0 w-screen xl:w-9/12 max-h-1/2 md:transform md:-translate-x-1/2 flex flex-col z-40 p-4 bg-neutral-700 text-white shadow-even shadow-black"
  >
    <h2
      bind:this={dialogHeader}
      class="text-xl font-bold mb-4 order-1"
      tabindex="-1"
    >
      Participate in our Research
    </h2>
    <div class="flex-1 flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-8 order-3 overflow-auto">
      <div class="md:w-3/6">
        <p>
          The Museum Map system is developed as part of an ongoing research
          project collaboration between researchers at the Open University and
          Edge Hill University. We are investigating how large digital cultural
          heritage collections can be made available to the general public. As
          part of this we are also interested in understanding how users explore
          such a digital collection and for this we would like to ask you for
          your consent to track your interactions on the Museum Map. If you are
          prepared to help us, then please use the consent button <span class="md:hidden">below</span><span class="hidden md:inline">on the right</span>
          to give your consent to collecting your data as outlined.
        </p>
      </div>
      <div class="md:w-3/6">
        <p>
          If you consent to participate, the following data will be collected:
        </p>
        <ul class="list-disc pl-8 pb-4">
          <li>Your browser version and operating system.</li>
          <li>All your interactions with the Museum Map system.</li>
          <li>Basic demographics data.</li>
        </ul>
        <p>Your data will be used for the following purposes:</p>
        <ul class="list-disc pl-8 pb-4">
          <li>
            Anonymised and cleaned data will be made available to the research
            community for future studies.
          </li>
          <li>
            Anonymised and cleaned data will be used in research publications.
          </li>
        </ul>
        <p class="pb-4">
          You can withdraw your consent at any point using the research icon in
          the bottom-left corner of the page.
        </p>
        <div class="flex flex-row">
          <div class="w-3/6 text-center">
            <button
              on:click={setConsent}
              class="inline-block {!$consent
                ? 'bg-neutral-600'
                : 'bg-blue-800'} px-4 lg:px-3 py-3 lg:py-1 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800"
              >I consent as outlined above</button
            >
            {#if $consent}
              <label class="block pt-4"
                >Please select your age band
                <select
                  bind:this={ageBandSelect}
                  class="inline-block bg-blue-800 px-2 py-1 rounded-lg"
                  bind:value={$ageBand}
                >
                  <option value="0">&lt; 18</option>
                  <option value="1">18 - 29</option>
                  <option value="2">30 - 39</option>
                  <option value="3">40 - 49</option>
                  <option value="4">50 - 59</option>
                  <option value="5">60 - 69</option>
                  <option value="6">70 - 79</option>
                  <option value="7">80 - 89</option>
                  <option value="8">90 - 99</option>
                  <option value="9">&gt; 99</option>
                </select>
              </label>
            {/if}
          </div>
          <div class="w-3/6 text-center">
            <button
              on:click={() => {
                consent.set(false);
              }}
              class="inline-block {$consent
                ? 'bg-neutral-600'
                : 'bg-blue-800'} px-4 lg:px-3 py-3 lg:py-1 rounded-lg lg:underline-offset-2 lg:hover:bg-blue-800 lg:focus:bg-blue-800"
              >I do not consent</button
            >
          </div>
        </div>
      </div>
    </div>
    {#if $tracker}
      <p bind:this={thankYouMessage} class="mb-4 text-md order-2" tabindex="-1">
        Thank you for contributing to the Museum Map project. Your input is much
        appreciated!
      </p>
    {/if}
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
