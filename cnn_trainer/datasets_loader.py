import numpy as np


class DatasetsLoader(object):
    @staticmethod
    def get_valid_train_set(path, file_numbers, rng):

        # neg_files = []
        # pos_files = []
        # for i in file_numbers:
        #     y = np.load(path + 'Y_' + str(i) + ".npy")
        #     if np.sum(y) > 0:
        #         pos_files.append(i)
        #     else:
        #         neg_files.append(i)
        #
        # print 'neg', len(neg_files)
        # print 'pos', len(pos_files)
        #
        # n_valid_neg = np.ceil(len(neg_files) / 3.5)
        # n_valid_pos = np.ceil(len(pos_files) / 4)
        #
        # valid_files = np.concatenate((
        # rng.choice(neg_files, size=n_valid_neg, replace=False), rng.choice(pos_files, size=n_valid_pos, replace=False)))
        # valid_idx = np.where(file_numbers == valid_files)

        all_x, all_y = None, None
        for f in file_numbers:
            x, y = DatasetsLoader.load(path, f)
            all_x = x if all_x is None else np.concatenate((all_x, x))
            all_y = y if all_y is None else np.concatenate((all_y, y))

        valid_idx = np.arange(0, 0)
        be = DatasetsLoader.get_begin_end(all_y)
        for i in range(len(be)):
            size = np.rint((be[i, 1] - be[i, 0]) / 5.0)
            begin = rng.randint(be[i, 0], be[i, 1] - size)
            valid_idx = np.concatenate((valid_idx, np.arange(begin, begin + size)))

        be = np.roll(be, 1)
        be = np.concatenate((be, [[be[0, 0], all_y.shape[0]]]))
        be[0, 0] = 0

        for i in range(len(be)):
            size = np.rint((be[i, 1] - be[i, 0]) / 5.0)
            begin = rng.randint(be[i, 0], be[i, 1] - size)
            valid_idx = np.concatenate((valid_idx, np.arange(begin, begin + size)))

        valid_idx = np.int64(valid_idx)
        valid_set = all_x[valid_idx], all_y[valid_idx]
        train_set = np.delete(all_x, valid_idx, 0), np.delete(all_y, valid_idx, 0)

        return {'valid': valid_set, 'train': train_set}

    @staticmethod
    def get_begin_end(x):
        be = np.where(np.logical_xor(x[:-1], x[1:]))[0] + 1
        if x[0] > 0:
            be = np.concatenate(([0], be))
        if x[-1] > 0:
            be = np.concatenate((be, [len(x)]))
        return np.reshape(be, (len(be) / 2, 2))

    @staticmethod
    def load(path, file_numbers, n_time_points=1000, n_channels=18):
        if file_numbers.shape == ():
            file_numbers = np.array([file_numbers], dtype='int32')
        x = 0
        y = 0
        for i in file_numbers:
            x_temp = np.load(path + 'X_' + str(i) + ".npy")
            x_temp = np.reshape(x_temp, (-1, n_time_points * n_channels), order='F')  # by columns
            y_temp = np.load(path + 'Y_' + str(i) + ".npy")
            y_temp = np.squeeze(y_temp)
            if i == file_numbers[0]:
                x = x_temp
                y = y_temp
            else:
                x = np.concatenate((x, x_temp), axis=0)
                y = np.concatenate((y, y_temp), axis=0)

        x = np.float32(x)
        y = np.int8(y)

        return x, y