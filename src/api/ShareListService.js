
import ApiService from './ApiService';

const SHARE_LIST_KEY = 'cc-share-lists';

const ShareListService = {
  /**
   * Implements an endpoint to create a list.
   */
  createList(params) {
    const imageIDs = params.images.map(image => image.id);
    const list = { title: params.listTitle, images: imageIDs };

    return ApiService.post('/list', list)
      .then(({ data }) => {
        const listID = this.getShareListID(data.url);
        const listURL = this.getShareListURL(listID);

        return this.saveListToLocalStorage(
          listID,
          data.auth,
          params.images[0].url,
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
    const list = JSON.parse(localStorage.getItem(SHARE_LIST_KEY));

    if (list) {
      list.reverse();
    }
    return Promise.resolve(list || []);
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
    return ApiService.post('/link_create', { url: params.url });
  },
  /**
   * Implements an endpoint to update a list.
   */
  updateList(params) {
    return ApiService.update('/list',
      params.id,
      params.images,
      { Authorization: `Bearer ${params.auth}` }
    );
  },
  /**
   * Implements an endpoint to delete a list.
   */
  deleteList(params) {
    ApiService.setHeader({ auth: params.auth });

    return ApiService.delete('/list', params.id);
  },
  /**
   * Implements an endpoint to get a list based on ID.
  */
  getList(params) {
    return ApiService.get('/list', params.id);
  },
};

export default ShareListService;
