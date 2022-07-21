<script lang="ts">
    import { Link } from 'svelte-navigator';

    export let item: JsonApiObject;
    export let noLink = false;
    export let noTitle = false;
    export let size = 'small';

    function imageLink(imageId: string[] | undefined): string {
        if (imageId) {
            return '/images/' + imageId.join('/') + (size === 'large' ? '' : '-240') + '.jpg';
        } else {
            return '';
        }
    }

    function linkTo(item: JsonApiObject) {
        if (item && item.relationships.room) {
            return '/room/' + (item.relationships.room.data as JsonApiObjectReference).id + '/' + item.id;
        } else {
            return '/';
        }
    }
</script>

{#if item !== null}
    {#if noLink}
        <div class="block h-full w-full overflow-hidden">
            <figure class="flex flex-col justify-center items-center h-full overflow-hidden">
                <img class="block shrink-1 grow-1 min-h-0" src={imageLink(item.attributes.images[0])} alt=""/>
                <figcaption class="flex-none max-w-full pt-2 text-center text-sm {noTitle ? 'sr-only' : ''}">{item.attributes.title}</figcaption>
            </figure>
        </div>
    {:else}
        <Link to={linkTo(item)} class="block h-full w-full overflow-hidden underline-offset-2 hover:img-brightness hover:underline focus:underline">
            <figure class="flex flex-col justify-center items-center h-full overflow-hidden">
                <img class="block shrink-1 grow-1 min-h-0 transition" src={imageLink(item.attributes.images[0])} alt=""/>
                <figcaption class="flex-none max-w-full pt-2 text-center text-sm {noTitle ? 'sr-only' : ''}">{item.attributes.title}</figcaption>
            </figure>
        </Link>
    {/if}
{/if}
