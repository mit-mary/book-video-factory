import { Img, staticFile } from "remotion";

export type AtlasCrop = {
  x: number;
  y: number;
  width: number;
  height: number;
};

export const DIRECTION_A_CROPS = {
  hook: { x: 18, y: 18, width: 482, height: 656 },
  detail: { x: 523, y: 18, width: 482, height: 656 },
  clock: { x: 18, y: 697, width: 312, height: 378 },
  hand: { x: 333, y: 697, width: 343, height: 378 },
  heart: { x: 679, y: 697, width: 326, height: 378 },
  turning: { x: 18, y: 1098, width: 482, height: 422 },
  ending: { x: 523, y: 1098, width: 482, height: 422 },
} satisfies Record<string, AtlasCrop>;

const ATLAS_WIDTH = 1024;
const ATLAS_HEIGHT = 1536;

export const DirectionAAtlasCrop: React.FC<{
  name: string;
  source: string;
  crop: AtlasCrop;
  targetWidth: number;
  targetHeight: number;
}> = ({ name, source, crop, targetWidth, targetHeight }) => {
  const scale = Math.max(targetWidth / crop.width, targetHeight / crop.height);
  const imageWidth = ATLAS_WIDTH * scale;
  const imageHeight = ATLAS_HEIGHT * scale;
  const imageLeft = targetWidth / 2 - (crop.x + crop.width / 2) * scale;
  const imageTop = targetHeight / 2 - (crop.y + crop.height / 2) * scale;
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden" }}>
      <Img
        name={name}
        src={staticFile(source)}
        style={{
          position: "absolute",
          left: imageLeft,
          top: imageTop,
          width: imageWidth,
          height: imageHeight,
          maxWidth: "none",
        }}
      />
    </div>
  );
};
