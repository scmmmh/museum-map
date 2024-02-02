<script lang="ts">
  import { tick } from "svelte";
  import { location } from "../simple-svelte-router";

  import { ageBand, track, localPreferences } from "../store";
  import Header from "../components/Header.svelte";
  import Footer from "../components/Footer.svelte";

  let age: string | null = null;
  let ageMissing: boolean = false;
  let gender: string | null = null;
  let genderMissing: boolean = false;
  let interest: string | null = null;
  let interestMissing: boolean = false;
  let visit: string | null = null;
  let visitMissing: boolean = false;

  async function saveDemographics(ev: Event) {
    ev.preventDefault();
    ageMissing = age === null;
    genderMissing = gender === null;
    interestMissing = interest === null;
    visitMissing = visit === null;
    if (!ageMissing && !genderMissing && !interestMissing && !visitMissing) {
      ageBand.set(age as string);
      localPreferences.setPreference("tracking.ageBand", age as string);
      track({
        action: "set-demographics",
        params: { age: age, gender: gender, interest: interest, visit: visit },
      });
      location.push("/");
    } else {
      await tick();
      const firstError = document.querySelector(
        "#content .error-message",
      ) as HTMLElement | null;
      if (firstError !== null) {
        firstError.scrollIntoView({ block: "center", behavior: "smooth" });
        firstError.focus();
      }
    }
  }
</script>

<Header title="Museum Map - About You" nav={[]} />
<article id="content" tabindex="-1" class="px-4 py-3">
  <h2 class="flex-1 py-2 text-xl font-bold" tabindex="-1">About You</h2>
  <p class="mb-6 max-w-[43rem]">
    Thank you very much for your support of our research. In order to understand
    how different groups use the Museum Map, we would like to ask you the
    following four quick questions regarding yourself:
  </p>
  <form on:submit={saveDemographics}>
    <h3
      tabindex="-1"
      class="text-lg font-bold mb-2 {ageMissing ? 'error-message' : ''}"
    >
      1. How old are you?
    </h3>
    {#if ageMissing}
      <p class="px-2 py-1 mb-2 max-w-[42rem] bg-red-800 rounded">
        Please select your age.
      </p>
    {/if}
    <div class="ml-4 text-lg lg:text-base">
      <label class="block mb-1">
        <input type="radio" name="age" value="0" bind:group={age} /> under 18
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="1" bind:group={age} /> 18 - 20
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="2" bind:group={age} /> 21 - 30
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="3" bind:group={age} /> 31 - 40
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="4" bind:group={age} /> 41 - 50
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="5" bind:group={age} /> 51 - 60
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="6" bind:group={age} /> 61 - 70
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="7" bind:group={age} /> 71 - 80
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="8" bind:group={age} /> 81 - 90
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="9" bind:group={age} /> 91 - 100
      </label>
      <label class="block mb-1">
        <input type="radio" name="age" value="10" bind:group={age} /> over 100
      </label>
    </div>
    <h3
      class="text-lg font-bold mb-2 mt-6 {genderMissing ? 'error-message' : ''}"
    >
      2. What gender do you primarily describe yourself as?
    </h3>
    {#if genderMissing}
      <p class="px-2 py-1 mb-2 max-w-[42rem] bg-red-800 rounded">
        Please select the gender you primarily describe yourself as.
      </p>
    {/if}
    <div class="ml-4 text-lg lg:text-base">
      <label class="block mb-1">
        <input type="radio" name="gender" value="female" bind:group={gender} /> Female
      </label>
      <label class="block mb-1">
        <input type="radio" name="gender" value="male" bind:group={gender} /> Male
      </label>
      <label class="block mb-1">
        <input
          type="radio"
          name="gender"
          value="non-binary"
          bind:group={gender}
        /> Non-binary
      </label>
      <label class="block mb-1">
        <input
          type="radio"
          name="gender"
          value="transgender"
          bind:group={gender}
        /> Transgender
      </label>
      <label class="block mb-1">
        <input
          type="radio"
          name="gender"
          value="no-response"
          bind:group={gender}
        /> Prefer not to respond
      </label>
      <label class="block mb-1">
        <input type="radio" name="gender" value="other" bind:group={gender} /> Other
      </label>
    </div>
    <h3
      class="text-lg font-bold mb-2 mt-6 {interestMissing
        ? 'error-message'
        : ''}"
    >
      3. How interested are you in museums or galleries?
    </h3>
    {#if interestMissing}
      <p class="px-2 py-1 mb-2 max-w-[42rem] bg-red-800 rounded">
        Please select how interested you are in museums or galleries.
      </p>
    {/if}
    <div class="ml-4 text-lg lg:text-base">
      <label class="block md:inline-block">
        <span class="hidden md:inline-block">Not interested at all</span>
        <input
          type="radio"
          name="interest"
          value="1"
          class="inline-block mr-2 md:mx-2"
          bind:group={interest}
        />
        <span class="inline-block md:hidden">Not interested at all</span>
      </label>
      <label class="block md:inline-block md:mx-2">
        <span class="sr-only">2</span>
        <input type="radio" name="interest" value="2" bind:group={interest} />
      </label>
      <label class="block md:inline-block md:mx-2">
        <span class="sr-only">2</span>
        <input type="radio" name="interest" value="3" bind:group={interest} />
      </label>
      <label class="block md:inline-block md:mx-2">
        <span class="sr-only">2</span>
        <input type="radio" name="interest" value="4" bind:group={interest} />
      </label>
      <label class="block md:inline-block">
        <input
          type="radio"
          name="interest"
          value="5"
          class="md:inline-block mr-2 md:mx-2"
          bind:group={interest}
        />
        Very interested
      </label>
    </div>
    <h3
      class="text-lg font-bold mb-2 mt-6 {visitMissing ? 'error-message' : ''}"
    >
      4. How often do you visit museums or galleries?
    </h3>
    {#if visitMissing}
      <p class="px-2 py-1 mb-2 max-w-[42rem] bg-red-800 rounded">
        Please select how often you visit museums or galleries.
      </p>
    {/if}
    <div class="ml-4 text-lg lg:text-base">
      <label class="block mb-1">
        <input type="radio" name="visit" value="0" bind:group={visit} /> At least
        once a week
      </label>
      <label class="block mb-1">
        <input type="radio" name="visit" value="1" bind:group={visit} /> At least
        once a month
      </label>
      <label class="block mb-1">
        <input type="radio" name="visit" value="2" bind:group={visit} /> At least
        once a year
      </label>
      <label class="block mb-1">
        <input type="radio" name="visit" value="3" bind:group={visit} /> Less frequently
      </label>
      <label class="block mb-1">
        <input type="radio" name="visit" value="4" bind:group={visit} /> Never
      </label>
    </div>
    <div class="mt-6 mb-4 flex flex-row max-w-[28rem]">
      <button
        type="button"
        class="inline-block px-4 lg:px-3 py-3 lg:py-1 rounded-lg lg:underline-offset-2 bg-neutral-600 lg:hover:bg-blue-800 lg:focus:bg-blue-800"
        >Withdraw Consent</button
      >
      <span class="flex-1"></span>
      <button
        type="submit"
        class="inline-block px-4 lg:px-3 py-3 lg:py-1 rounded-lg lg:underline-offset-2 bg-blue-800 lg:hover:bg-blue-800 lg:focus:bg-blue-800"
        >Save my Responses</button
      >
    </div>
  </form>
</article>
<Footer />
