<script lang="ts">
    import { onDestroy, tick } from "svelte";
    import {
      localPreferences,
      consent,
      ageBand,
    } from "../store";

    // Dialog defaults to visible, if the dialog has never been shown before
    let ageBandSelect: HTMLSelectElement | null = null;

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
      localPreferences.setPreference("tracking.ageBand", ageBand);
    });

    onDestroy(() => {
      consentUnsubscribe();
      ageBandUnsubscribe();
    });
  </script>

      <div
        class="flex-1 flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-8 order-3 overflow-auto"
      >
        <div class="md:w-3/6">
          <p>
            The Museum Map system is developed as part of an ongoing research
            project collaboration between researchers at the Open University and
            Edge Hill University. We are investigating how large digital cultural
            heritage collections can be made available to the general public. As
            part of this we are also interested in understanding how users explore
            such a digital collection and for this we would like to ask you for
            your consent to track your interactions on the Museum Map. If you are
            prepared to help us, then please use the consent button <span
              class="md:hidden">below</span
            ><span class="hidden md:inline">on the right</span>
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