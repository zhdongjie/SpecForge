package org.eu.originalkeen.core.utils;

import org.eu.originalkeen.core.config.properties.OriginalProperties;
import org.eu.originalkeen.core.exception.system.FileReadException;
import org.eu.originalkeen.core.exception.system.FileWriteException;
import lombok.extern.slf4j.Slf4j;

import java.io.IOException;
import java.nio.file.*;
import java.util.Objects;

/**
 * 文件工具类
 * 提供文件读写、类型校验和远程文件获取等功能
 */
@Slf4j
public class FileUtils {

    /**
     * 如果文件不存在，则将文本写入文件
     * 先校验文件是否存在，如果不存在则创建并写入内容
     *
     * @param filePath 文件路径
     * @param content  要写入的文本内容
     * @throws FileWriteException 写入文件失败时抛出
     */
    public static void writeTextToFileIfNotExists(String filePath, String content) {
        try {
            Path path = Paths.get(filePath);
            Path parentDir = path.getParent();
            createDirectoriesIfNotExist(parentDir);

            if (Files.notExists(path)) {
                Files.writeString(path, content, StandardOpenOption.CREATE_NEW);
                log.info("File created and content written: {}", filePath);
            } else {
                log.info("File already exists: {}", filePath);
            }
        } catch (IOException | InvalidPathException exception) {
            log.error("Failed to write file [{}]: {}", filePath, exception.getMessage(), exception);
            throw new FileWriteException(exception.getMessage(), exception);
        }
    }

    /**
     * 读取文件内容为字符串
     * 将文件的全部内容读取为字符串
     *
     * @param filePath 文件路径
     * @return 文件内容字符串
     * @throws FileReadException 读取文件失败时抛出
     */
    public static String readFileToString(String filePath) {
        try {
            Path path = Paths.get(filePath);
            String content = Files.readString(path);
            log.info("Read {} bytes from file: {}", content.length(), filePath);
            return content;
        } catch (IOException | InvalidPathException exception) {
            log.error("Failed to read file [{}]: {}", filePath, exception.getMessage(), exception);
            throw new FileReadException(exception.getMessage(), exception);
        }
    }

    /**
     * 如果目录不存在则创建
     * 校验目录是否存在，如果不存在则创建目录及其父目录
     *
     * @param dir 要创建的目录路径
     * @throws FileWriteException 创建目录失败时抛出
     */
    private static void createDirectoriesIfNotExist(Path dir) {
        if (Objects.nonNull(dir) && Files.notExists(dir)) {
            try {
                Files.createDirectories(dir);
                log.info("Created directory: {}", dir.toAbsolutePath());
            } catch (IOException exception) {
                log.error("Failed to create directory: {}", dir, exception);
                throw new FileWriteException(exception.getMessage(), exception);
            }
        }
    }

    /**
     * 私有构造函数
     * 防止实例化工具类
     */
    private FileUtils() {
    }

}
