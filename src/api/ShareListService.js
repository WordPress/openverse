
import ApiService from './ApiService';

const SHARE_LIST_KEY = 'cc-share-lists';

const ShareListService = {
  /**
   * Implements an endpoint to create a list.
   */
  createList(params) {
    const list = { title: params.listTitle, images: [params.image.id] };

    return ApiService.post('/list', list)
      .then(({ data }) => {
        const listID = this.getShareListID(data.url);
        const listURL = this.getShareListURL(listID);

        return this.saveListToLocalStorage(
          listID,
          data.auth,
          params.image.url,
          listURL,
        ).then((lists) => { lists.reverse(); return { lists }; });
      });
  },
  getShareListID(url) {
    return url.match(/\/(?:list\/)(.*)/)[1];
  },
  getShareListURL(listID) {
    const shareURL = `/lists/${listID}`;

    return location.origin + shareURL;
  },
  /**
   * Implements an endpoint to gets all lists from local storage.
   */
  getListsFromLocalStorage() {
    const lists = JSON.parse(localStorage.getItem(SHARE_LIST_KEY));

    if (lists) {
      lists.reverse();
    }
    return Promise.resolve(lists || []);
  },
  /**
   * Implements a method to get an auth token.
   */
  getAuthTokenFromLocalStorage(listID) {
    const lists = JSON.parse(localStorage.getItem(SHARE_LIST_KEY));
    const listWithToken = lists.find(list => list.listID === listID);
    let authToken;

    if (listWithToken) {
      authToken = listWithToken.auth;
    }

    return Promise.resolve(authToken);
  },
  /**
   * Implements an endpoint to delete the list from local storage.
   */
  deleteListFromLocalStorage() {
    return this.getListsFromLocalStorage()
      .then(lists => localStorage.setItem(SHARE_LIST_KEY, JSON.stringify(lists)));
  },
  /**
   * Implements an endpoint to save the list to local storage.
   */
  saveListToLocalStorage(listID, auth, thumbnail, url) {
    return this.getListsFromLocalStorage()
      .then((lists) => {
        lists.push({ listID, auth, thumbnail, url });
        localStorage.setItem(SHARE_LIST_KEY, JSON.stringify(lists));

        return lists;
      });
  },
  /**
   * Implements an endpoint to create a shortened list url.
   */
  createShortenedListURL(params) {
    return ApiService.post('/link', { url: params.url });
  },
  /**
   * Implements an endpoint to update a list.
   */
  updateList(params) {
    return ApiService.update('/list',
      params.id,
      { images: params.images },
      { Authorization: `Token ${params.auth}` },
    );
  },
  /**
   * Implements an endpoint to delete a list.
   */
  deleteList(params) {
    return ApiService.delete('/list',
      params.id,
      { images: params.images },
      { Authorization: `Token ${params.auth}` },
    );
  },
  /**
   * Implements an endpoint to get a list based on ID.
  */
  getList(params) {
    return ApiService.get('/list', params.id);
  },
};

export default ShareListService;
