<script lang="ts">
    import { config } from "../store";
</script>

<footer class="bg-inherit shadow-even shadow-black text-sm py-1 z-10">
    <nav>
        <ul class="flex flex-row flex-wrap gap-y-1">
            <li class="flex-none w-full md:w-1/3 px-2 text-center md:text-left">
                <a
                    href="https://www.room3b.eu/pages/projects/digital-museum-map.html"
                    target="_blank"
                    rel="noopener"
                    class="underline decoration-dotted hover:decoration-solid focus:decoration-solid"
                    >Find out more about how this works</a
                >
            </li>
            <li
                class="flex-none w-full md:w-1/3 pt-1 md:pt-0 md:py-0 text-center"
            >
                {#if $config && $config.footer && $config.footer.center}
                    {#if $config.footer.center.url}
                        <a
                            href={$config.footer.center.url}
                            target="_blank"
                            rel="noopener"
                            class="underline decoration-dotted hover:decoration-solid focus:decoration-solid"
                            >{@html $config.footer.center.label}</a
                        >
                    {:else}
                        <span>{@html $config.footer.center.label}</span>
                    {/if}
                {/if}
            </li>
            <li
                class="flex-none w-full md:w-1/3 px-2 pt-1 md:pt-0 text-center md:text-right"
            >
                {#if $config && $config.footer && $config.footer.right}
                    {#if $config.footer.right.url}
                        <a
                            href={$config.footer.right.url}
                            target="_blank"
                            rel="noopener"
                            class="underline decoration-dotted hover:decoration-solid focus:decoration-solid"
                            >{@html $config.footer.right.label}</a
                        >
                    {:else}
                        <span>{@html $config.footer.right.label}</span>
                    {/if}
                {/if}
            </li>
        </ul>
    </nav>
</footer>
