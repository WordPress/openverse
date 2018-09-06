
import ApiService from './ApiService';

const SHARE_LIST_KEY = 'cc-share-lists';

const ShareListService = {
  /**
   * Implements an endpoint to create a list.
   */
  createList(params) {
    const list = { title: params.listTitle, images: params.images };

    return ApiService.post('/list', list);
  },
  /**
   * Implements an endpoint to gets all lists from local storage.
   */
  getListsFromLocalStorage() {
    const list = JSON.parse(localStorage.getItem(SHARE_LIST_KEY));

    return Promise.resolve(list);
  },
  /**
   * Implements an endpoint to delete the list to local storage.
   */
  deleteListToLocalStorage(listID) {
    let lists = this.getListsFromLocalStorage();
    delete lists[listID];
    localStorage.setItem(SHARE_LIST_KEY, JSON.stringify(lists));

    return Promise.resolve(lists);
  },
  /**
   * Implements an endpoint to save the list to local storage.
   */
  saveListToLocalStorage(listID, listAuthToken) {
    let lists = this.getListsFromLocalStorage();
    lists[listID] = listAuthToken;
    localStorage.setItem(SHARE_LIST_KEY, JSON.stringify(lists));

    return Promise.resolve(lists);
  },
  /**
   * Implements an endpoint to create a shortened list url.
   */
  createShortenedListURL(params) {
    return ApiService.post('/link_create', { url: params.url });
  },
  /**
   * Implements an endpoint to edit a list.
   */
  editList(params) {
    ApiService.setHeader({ auth: params.auth });

    return ApiService.update('/list_update', params.id, params.ids);
  },
  /**
   * Implements an endpoint to delete a list.
   */
  deleteList(params) {
    ApiService.setHeader({ auth: params.auth });

    return ApiService.delete('/list_delete', params.id);
  },
  /**
   * Implements an endpoint to get a list based on ID.
  */
  getList(params) {
    return ApiService.get('/list', params.id);
  },
};

export default ShareListService;
