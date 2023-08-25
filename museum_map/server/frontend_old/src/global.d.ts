/// <reference types="svelte" />

/**
 * Generic JSONAPI types.
 */
 type JsonApiResponse = {
    data?: JsonApiObject | JsonApiObject[],
    errors?: JsonApiError[],
};

type JsonApiObject = {
    type: string,
    id?: string,
    attributes?: JsonApiAttributeDict,
    relationships?: {[key: string]: JsonApiObjectRelationship}
};

type JsonApiAttributeDict = {
    [key: string]: any,
};

type JsonApiObjectRelationship = {
    data: JsonApiObjectReference | JsonApiObjectReference[];
}

type JsonApiObjectReference = {
    type: string;
    id: string;
}

type JsonApiError = {
    status: string,
    code?: string,
    title: string,
    detail?: string,
    source?: JsonApiErrorSource,
};

type JsonApiErrorSource = {
    pointer: string,
};
