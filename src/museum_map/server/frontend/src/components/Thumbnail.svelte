<script lang="ts">
    import { Link } from 'svelte-navigator';

    export let item: JsonApiObject;
    export let hoverTitle = true;
    export let hideTitle = false;
    export let noLink = false;
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
        <div class="block h-full relative overflow-hidden bg-black">
            <figure class="flex flex-row w-full h-full justify-center {hoverTitle ? 'title-hover' : ''}">
                <img src={imageLink(item.attributes.images[0])} alt="" class="self-center max-w-full max-h-full"/>
                <figcaption class="absolute left-0 bottom-0 w-full px-2 py-1 bg-neutral-700 bg-opacity-80 {hideTitle ? 'sr-only' : ''}">{item.attributes.title}</figcaption>
            </figure>
        </div>
    {:else}
        <Link to={linkTo(item)} class="block h-full relative overflow-hidden bg-black">
            <figure class="flex flex-row w-full h-full justify-center {hoverTitle ? 'title-hover' : ''}">
                <img src={imageLink(item.attributes.images[0])} alt="" class="self-center max-w-full max-h-full"/>
                <figcaption class="absolute left-0 bottom-0 w-full px-2 py-1 bg-neutral-700 bg-opacity-80 {hideTitle ? 'sr-only' : ''}">{item.attributes.title}</figcaption>
            </figure>
        </Link>
    {/if}
{/if}
