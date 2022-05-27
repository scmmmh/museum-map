<script lang="ts">
    import { config } from '../store';
</script>

<footer class="sticky bottom-0 bg-inherit shadow-even shadow-black text-sm py-1 z-10">
    <nav>
        <ul class="flex flex-row flex-wrap gap-y-1">
            <li role="presentation" class="flex-none w-full md:w-1/3 px-2 text-center md:text-left">
                <a href="https://www.room3b.eu/pages/projects/digital-museum-map.html" target="_blank" rel="noopener" class="hover:underline focus:underline">Find out more about how this works</a>
            </li>
            <li role="presentation" class="flex-none w-full md:w-1/3 px-2 text-center">
                {#if $config && $config.attributes.footer && $config.attributes.footer.center}
                    {#if $config.attributes.footer.center.url}
                        <a href="{$config.attributes.footer.center.url}" target="_blank" rel="noopener" class="hover:underline focus:underline">{@html $config.attributes.footer.center.label}</a>
                    {:else}
                        <span>{@html $config.attributes.footer.center.label}</span>
                    {/if}
                {/if}
            </li>
            <li role="presentation" class="flex-none w-full md:w-1/3 px-2 text-center md:text-right">
                {#if $config && $config.attributes.footer && $config.attributes.footer.right}
                    {#if $config.attributes.footer.right.url}
                    <a href="{$config.attributes.footer.right.url}" target="_blank" rel="noopener" class="hover:underline focus:underline">{@html $config.attributes.footer.right.label}</a>
                {:else}
                    <span>{@html $config.attributes.footer.right.label}</span>
                {/if}
            {/if}
            </li>
        </ul>
    </nav>
</footer>
